#!/usr/bin/python

import argparse
import json
import os
import os.path as op
import subprocess as sp
import sys

import docker

import slugid

DATA_DIR='fetch'

def extract_urls(command):
    """Extract all the urls and replace them with slugids
    so that we can download the files locally."""
    parts = command.split(' ')
    to_fetch = {}
    for i,part in enumerate(parts):
        if (part.startswith("https://") or part.startswith("http://") or part.startswith("http://")):
            filename = part.split('/')[-1]
            to_fetch[part] = f"{DATA_DIR}/{filename}"
            parts[i] = to_fetch[part]

    return parts, to_fetch

def fetch_file(url):
    sp.call([
        'wget', '-NP', 'fetch', url
    ])


def main():
    parser = argparse.ArgumentParser(description="""

    python executor.py conf.json
""")

    parser.add_argument('conf')
    #parser.add_argument('-o', '--options', default='yo',
    #                    help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()

    with open(args.conf) as f:
        conf = json.load(f)


    if not op.exists('fetch'):
        os.makedirs('fetch')

    [cmd_parts, to_fetch] = extract_urls(conf['command'])
    filenames = {}

    for url,filename in to_fetch.items():
        fetch_file(url)

    print("cmd_parts", cmd_parts)
    sp.call(cmd_parts)
    # for filename in conf['fetch']:
    #     sp.call([
    #         'wget', '-PN', 'fetch', filename["url"],
    #         "-O", filename["as"]
    #     ])

    

if __name__ == '__main__':
    main()

