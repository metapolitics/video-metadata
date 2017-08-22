#!/usr/local/bin/python3
from __future__ import division
import subprocess
import shlex
import json
import os
import inspect 

def findVideoMetadata(pathToInputVideo):
    try:
        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = shlex.split(cmd)
        args.append(pathToInputVideo)
        # run the ffprobe process, decode stdout into utf-8 & convert to JSON
        ffprobeOutput = subprocess.check_output(args).decode('utf-8')
        ffprobeOutput = json.loads(ffprobeOutput)
        height = ffprobeOutput['streams'][0]['height']
        width = ffprobeOutput['streams'][0]['width']
        video_codec = ffprobeOutput['streams'][0]['codec_name']
        video_bitrate = ffprobeOutput['streams'][0]['bit_rate']
        audio_codec = ffprobeOutput['streams'][1]['codec_name']
        audio_channels = ffprobeOutput['streams'][1]['channels']
        audio_format = ffprobeOutput['streams'][1]['channel_layout']
        audio_bitrate = ffprobeOutput['streams'][1]['bit_rate']
        #return CSV for storage
        return str(video_codec) + '|' + str(video_bitrate) + '|' + str(height) + '|' + str(width) + '|' + str(audio_codec) + '|' + str(audio_bitrate) + '|' + str(audio_channels) + '|' + audio_format
    except Exception as e:
        return pathToInputVideo

def recursiveScan(path):
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            try:
                f.write(filename + '|' + findVideoMetadata(os.path.join(dirname, filename)) + os.linesep)
                pass
            except Exception as e:
                print("Error with File: " + os.path.join(dirname, filename))
        for subdirname in dirnames:
            recursiveScan(os.path.join(dirname, subdirname))

testPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"
csvFile = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/video_utils.csv"

f = open(csvFile, 'w')
recursiveScan(testPath)
f.close()