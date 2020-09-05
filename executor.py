#!/usr/bin/python

import argparse
import hashlib
import json
import os
import os.path as op
import subprocess as sp
import sys
from hashlib import sha256

import docker

import slugid

DATA_DIR='fetch'

def fetch_dir(base_dir):
    return op.join(base_dir, '.fetch')

def extract_urls(command, base_dir):
    """Extract all the urls and replace them with slugids
    so that we can download the files locally."""
    parts = command.split(' ')
    to_fetch = {}
    for i,part in enumerate(parts):
        if (part.startswith("https://") or part.startswith("http://") or part.startswith("http://")):
            filename = part.split('/')[-1]
            to_fetch[part] = op.join('.fetch',filename)
            parts[i] = to_fetch[part]

    return parts, to_fetch

def fetch_file(url, base_dir):
    sp.call([
        'wget', '-NP', fetch_dir(base_dir), url
    ])

def save_steps(steps, base_dir):
    steps_file = op.join(base_dir, '.steps')

    with open(steps_file, 'w') as f:
        json.dump(steps, f)

def load_steps(base_dir):
    steps_file = op.join(base_dir, '.steps')

    if op.exists(steps_file):
        with open(steps_file, 'r') as f:
            steps = json.load(f)
            return steps
    return None

def main():
    parser = argparse.ArgumentParser(description="""

    python executor.py conf_dir
""")

    parser.add_argument('conf_dir')
    #parser.add_argument('-o', '--options', default='yo',
    #                    help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()
    base_dir = args.conf_dir

    with open(op.join(args.conf_dir, 'conf.cut')) as f:
        conf = f.readlines()

    fetch_dir = op.join(args.conf_dir, 'fetch')
    if not op.exists(fetch_dir):
        os.makedirs(fetch_dir)

    steps = load_steps(base_dir)

    for i,line in enumerate(conf):
        prior_commands = "".join(conf[:i+1])
        cmd_hash = sha256(prior_commands.encode('utf8')).hexdigest()
        if cmd_hash in steps and steps[cmd_hash]:
            print("skipping", line)
            continue

        [cmd_parts, to_fetch] = extract_urls(line.strip(), base_dir)
        filenames = {}

        for url,filename in to_fetch.items():
            fetch_file(url, base_dir)

        # print("cmd_parts", cmd_parts)
        cmd = " ".join(cmd_parts)
        sp.call(cmd, shell=True, cwd=args.conf_dir)

        steps[cmd_hash] = True
        save_steps(steps, base_dir)
        # sp.call(cmd_parts)
    # for filename in conf['fetch']:
    #     sp.call([
    #         'wget', '-PN', 'fetch', filename["url"],
    #         "-O", filename["as"]
    #     ])

    

if __name__ == '__main__':
    main()
