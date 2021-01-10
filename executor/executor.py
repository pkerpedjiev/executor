#!/usr/bin/python

import argparse
import hashlib
import json
import os
import os.path as op
import shlex
import subprocess as sp
import sys
from hashlib import sha256
from pathlib import Path

import docker

import slugid

DATA_DIR = "fetch"


def fetch_dir(base_dir):
    return op.join(base_dir, ".fetch")


def extract_urls(command, base_dir):
    """Extract all the urls and replace them with slugids
    so that we can download the files locally."""
    parts = command.split(" ")
    to_fetch = {}
    for i, part in enumerate(parts):
        if (
            part.startswith("https://")
            or part.startswith("http://")
            or part.startswith("http://")
        ):
            filename = part.split("/")[-1]
            to_fetch[part] = op.join(".fetch", filename)
            parts[i] = to_fetch[part]

    return parts, to_fetch


def fetch_file(url, base_dir):
    sp.call(["wget", "-NP", fetch_dir(base_dir), url])


def save_steps(steps, base_dir):
    steps_file = op.join(base_dir, ".steps")

    with open(steps_file, "w") as f:
        json.dump(steps, f, indent=2)


def load_steps(base_dir):
    steps_file = op.join(base_dir, ".steps")

    if op.exists(steps_file):
        with open(steps_file, "r") as f:
            steps = json.load(f)
            return steps

    return {}


def check_for_var_def(line):
    """Check if this line defines a variable."""
    s = shlex.shlex(line, posix=True, punctuation_chars=True)
    s.whitespace_split = True

    slist = list(s)

    if len(slist) == 1:
        parts = slist[0].split("=")
        if len(parts) == 2:
            key = parts[0]
            value = parts[1]

            return {key: value}

    return {}


def execute(conf_file):
    if conf_file is None:
        conf_file = Path.cwd() / "conf.cut"
    else:
        conf_file = Path(conf_file)

    with open(conf_file) as f:
        conf = f.readlines()

    base_dir = conf_file.parents[0]

    fetch_dir = op.join(base_dir, "fetch")
    if not op.exists(fetch_dir):
        os.makedirs(fetch_dir)

    steps = load_steps(base_dir)

    all_envs = {}
    prev_line = ""

    for i, line in enumerate(conf):
        line = f"{prev_line} {line}"
        prev_line = ""

        # combine multi-line commands
        if len(line.strip()) and line.strip()[-1] == "\\":
            prev_line = line
            continue

        # check to see if the line defines a variable
        envs = check_for_var_def(line)

        if len(envs.keys()):
            all_envs = {**all_envs, **envs}
            continue

        prior_commands = "".join(conf[: i + 1])
        cmd_hash = sha256(prior_commands.encode("utf8")).hexdigest()
        if cmd_hash in steps:
            same_envs = True

            # go through all currently defined env vars
            for env in all_envs:
                if "envs" in steps[cmd_hash]:
                    # if this step didn't have the same env definition
                    # then we need to replay it
                    if steps[cmd_hash]["envs"][env] != all_envs[env]:
                        same_envs = False
                else:
                    same_envs = False

            if same_envs:
                print("skipping", cmd_hash, line)
                continue

        # print("cmd_parts", cmd_parts)
        cmd = line.strip()

        if not len(line):
            continue

        ret = sp.run(
            cmd,
            shell=True,
            cwd=base_dir,
            executable="/bin/bash",
            env={**os.environ, **all_envs},
        )

        if ret.returncode != 0:
            print("error, quitting...")
            return

        steps[cmd_hash] = {"cmd": cmd, "envs": all_envs}
        save_steps(steps, base_dir)
        # sp.call(cmd_parts)
    # for filename in conf['fetch']:
    #     sp.call([
    #         'wget', '-PN', 'fetch', filename["url"],
    #         "-O", filename["as"]
    #     ])


if __name__ == "__main__":
    main()
