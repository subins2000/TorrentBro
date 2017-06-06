#!usr/bin/env python3

import os
import shutil

baseDir = os.path.dirname(os.path.abspath(__file__))

'''
Remove untracked and ignored files
'''
os.system('cd {baseDir};git clean -d -x -f'.format(
    baseDir=baseDir
))

'''
Remove .gitignore files
'''
for root, dirs, files in os.walk(baseDir):
    for d in dirs:
        if "__pycache__" in d:
            shutil.rmtree(os.path.join(root, d))

    for f in files:
        if ".gitignore" in f:
            os.remove(os.path.join(root, file))


'''
Build
'''
os.system('python3 {buildPy} build'.format(
    buildPy=baseDir + '/build.py'
))
