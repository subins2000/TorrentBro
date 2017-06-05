'''
Prepare a separate folder for debian packaging
'''

import argparse
import os
import shutil

parser = argparse.ArgumentParser(
    description='Prepare TorrentBro for Debian packaging')
parser.add_argument('--root', type=str, help='Target location')

args = parser.parse_args()

projectRoot = os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + '/../../')
target = args.root

shutil.copytree(projectRoot, target)

'''
Remove git files
'''
for root, dirs, files in os.walk(target):
    for d in dirs:
        if ".git" in d:
            shutil.rmtree(os.path.join(root, d))

    for f in files:
        if ".gitignore" in f:
            os.remove(os.path.join(root, f))
