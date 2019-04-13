#!/usr/local/bin/python3
from __future__ import division
from collections import defaultdict
import subprocess
import shlex
import json
import os
import inspect
import time
import sys
import hashlib
import sys
import logging

def progbar(curr, total, full_progbar, mode, text):
    frac = curr/total
    filled_progbar = round(frac*full_progbar)
    print('\r', '#'*filled_progbar + '-'*(full_progbar-filled_progbar), '[{:>7.2%}]'.format(frac), '[' + mode + ']', \
          '[{file:''<50}]'.format(file=text[:50]), end='')
    sys.stdout.flush()

def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def getVideoMetadata(pathToInputVideo):
    try:
        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = shlex.split(cmd)
        args.append(pathToInputVideo)
        # run the ffprobe process, decode stdout into utf-8 & convert to JSON
        ffprobeOutput = subprocess.check_output(args).decode('utf-8')
        ffprobeOutput = json.loads(ffprobeOutput)
        output = []
        output.append(str(ffprobeOutput['streams'][0]['height']))
        output.append(str(ffprobeOutput['streams'][0]['width']))
        output.append(str(ffprobeOutput['streams'][0]['codec_name']))
        output.append(str(ffprobeOutput['streams'][0]['bit_rate']))
        output.append(str(ffprobeOutput['streams'][1]['codec_name']))
        output.append(str(ffprobeOutput['streams'][1]['channels']))
        output.append(str(ffprobeOutput['streams'][1]['channel_layout']))
        output.append(str(ffprobeOutput['streams'][1]['bit_rate']))
        return ','.join(output)
    except Exception as e:
        return "NA,NA,NA,NA,NA,NA,NA,NA"


dirPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
csvFile = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep + "hash.csv"
fileList = []
shaDict = {}
shaList = {}
simplenameDict = {}
pathList = []


if len(sys.argv) > 1:
    if os.path.exists(dirPath + os.sep + str(sys.argv[1])):
        print("Opening file \'" + str(sys.argv[1]) + "\' for processing ... ")
        with open(dirPath + os.sep + str(sys.argv[1])) as openfileobject:
            for line in openfileobject:
                pathList.append(line.rstrip())
else:
    pathList.append(dirPath)
print("Scanning " + str(len(pathList)) + " directory structure" if len(pathList) > 0 else "")



print("Counting files ... ", end="")
sys.stdout.flush()
totalFiles = 0
for path in pathList:
    for root, dirs, files in os.walk(path, topdown=False):
        totalFiles += len(files)
print(str(totalFiles) + " found.")



print("Getting file hashes and duplicates ... ")
count = 0
# get full list list and generate hashes and filenames
for path in pathList:
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            count += 1
            progbar(count, totalFiles, 30, 'HASH' ,os.path.basename(os.path.join(root, name)))
            filepath = os.path.join(root, name)
            try:
                checksum = str(sha256_checksum(filepath))
            except:
                checksum = "0"

            if checksum in shaDict:
                shaDict[checksum] = shaDict[checksum] + 1
            else:
                shaDict[checksum] = 1
            shaList[filepath] = checksum

            simpleName = os.path.splitext(os.path.basename(filepath))[0]
            if simpleName in simplenameDict:
                simplenameDict[simpleName] = simplenameDict[simpleName] + 1
            else:
                simplenameDict[simpleName] = 1



sys.stdout.write("\n")
count = 0
print("Getting video file metadata ... ")
# get video metadata
for path in pathList:
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            count += 1
            progbar(count, totalFiles, 30, 'META' ,os.path.basename(os.path.join(root, name)))
            filepath = os.path.join(root, name)
            checksum = shaList[filepath]
            simpleName = os.path.splitext(os.path.basename(filepath))[0]
            # checksum, checksum occurances, simplename, simplename occurances, filesize, filepath, metadata"
            fileList.append(checksum + "," + str(shaDict[checksum]) + ",\"" + simpleName + "\"," + str(simplenameDict[simpleName]) + \
                            "," + str(os.path.getsize(filepath)) + ",\"" + os.path.basename(filepath) + "\",\"" + \
                            filepath + "\"," + getVideoMetadata(filepath))


sys.stdout.write("\n")
print("Writing to file ... ", end="")
sys.stdout.flush()


fileList.sort()
f = open(csvFile, 'w')
f.write("checksum,checksum occurances,simplename,simplename occurances,filesize,filename,filepath," + \
        "v-height,v-width,v-codec,v-bitrate,a-codec,a-channels,a-layout,a-bitrate" + os.linesep)
for item in fileList:
    try: # incase of error writing line
        f.write(item + os.linesep)
    except:
        logging.warning('Failed to log:' + item)
f.close()

print("complete")
