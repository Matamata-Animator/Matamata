import time
from subprocess import Popen
import os
import json
from PIL import Image
import sys
import cv2 as cv
import numpy as np
import shutil
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('-a', '--audio', required=True)
parser.add_argument('-t', '--text', required=True)
parser.add_argument('-o', '--output', required=False, default='output.mp4')
parser.add_argument('-s', '--offset', required=False, default='0.8')

args = parser.parse_args()

if os.path.isdir('generate'):
    shutil.rmtree('generate')
os.system('docker kill gentle')
os.system('docker rm gentle')
os.mkdir('generate')
time.sleep(1)
docker = Popen(['docker', 'run','--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(3)
r = os.popen('curl -F "audio=@' + (args.audio) +'" -F "transcript=@' + (args.text) + '" "http://localhost:8765/transcriptions?async=false"').read()
phoneReference = json.load(open('phonemes.json', encoding='utf8'))
characters = json.load(open('characters.json', encoding='utf8'))

facePath = 'faces/dumb-smile.png'
mouthPath = 'mouths/closed.png'

totalTime = 0;

stamps = json.loads(r)
counter = 0
videoList = open('generate/videos.txt', 'w+')


def createVideo(fPath, mPath, xPos, yPos, time, frame):
    global totalTime
    time = max(0.001, time)
    totalTime += time
    image = cv.imread(fPath, 0)
    face =  Image.open(fPath).convert("RGBA")
    mouth = Image.open(mPath).convert("RGBA")
    width = image.shape[1]
    height = image.shape[0]
    mouthPos = [xPos, yPos]
    face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
    face.save("generate/" + str(counter) + '.png')
    os.popen("ffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(time) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(frame) + ".mp4")
    print("\n\n\n\nffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(time) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(frame) + ".mp4\n\n\n\n\n\n")
    videoList.write("file '" + str(frame) + ".mp4'\n")
    return frame + 1



#Make mouth closed until first phoname
counter = createVideo(facePath, mouthPath, characters['stupid'][0]['x'], characters['stupid'][0]['y'], round(stamps['words'][0]['start'], 4) - float(args.offset), counter)

for w in range(len(stamps['words'])):
    word = stamps['words'][w]
    print(word['alignedWord'])
    wordTime = 0
    for p in range(len(word['phones'])):
        #Identify current phone
        phone = (word['phones'][p]['phone']).split('_')[0]
        wordTime += word['phones'][p]['duration']
        #Referance phonemes.json to see which mouth goes with which phone
        mouthPath = "mouths/" + (phoneReference['phonemes'][phone]['image'])

        facePath = "faces/dumb-smile.png"

        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]

        counter = createVideo(facePath, mouthPath, mouthPos[0], mouthPos[1], word['phones'][p]['duration'], counter)
    if (w < len(stamps['words']) - 1):
        mouthPath = 'mouths/closed.png'
        face =  Image.open(facePath).convert("RGBA")
        mouth = Image.open(mouthPath).convert("RGBA")
        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]

        counter = createVideo(facePath, mouthPath, mouthPos[0], mouthPos[1], round(stamps['words'][w + 1]['start'], 4) - totalTime - float(args.offset), counter)
#Combine all videos into one video
videoList.flush()

os.popen("ffmpeg -i " + str(args.audio) + " -f concat -safe 0 -i generate/videos.txt -c copy " + str(args.output)).read()
print("ffmpeg -i " + str(args.audio) + " -f concat -safe 0 -i generate/videos.txt -c copy " + str(args.output))
time.sleep(1)
if os.path.isdir('generate'):
    shutil.rmtree('generate')
os.system('docker kill gentle')
os.system('docker rm gentle')
