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

stamps = json.loads(r)
counter = 0
videoList = open('generate/videos.txt', 'w+')


def createVideo(fPath, mPath, xPos, yPos, frame):
    image = cv.imread(fPath, 0)
    face =  Image.open(fPath).convert("RGBA")
    mouth = Image.open(mPath).convert("RGBA")
    width = image.shape[1]
    height = image.shape[0]
    mouthPos = [xPos, yPos]
    face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
    face.save("generate/" + str(counter) + '.png')
    os.popen("ffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(round(stamps['words'][0]['start'], 4)) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(frame) + ".mp4")
    videoList.write("file '" + str(frame) + ".mp4'\n")
    return frame + 1



#Make mouth closed until first phoname
counter = createVideo(facePath, mouthPath, characters['stupid'][0]['x'], characters['stupid'][0]['y'], counter)


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

        image = cv.imread(facePath, 0)

        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]

        counter = createVideo(facePath, mouthPath, mouthPos[0], mouthPos[1], counter)
    if (w < len(stamps['words']) -1):
        mouthPath = 'mouths/closed.png'
        face =  Image.open(facePath).convert("RGBA")
        mouth = Image.open(mouthPath).convert("RGBA")
        width = image.shape[1]
        height = image.shape[0]
        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]
        face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
        face.save("generate/" + str(counter) + '.png')

        os.popen("ffmpeg -loop 1 -i generate/" + str(counter) + ".png -c:v libx264 -t " + str((round(stamps['words'][w + 1]['start'], 4) - round(stamps['words'][w]['end'], 4))) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(counter) + ".mp4")
        videoList.write("file '" + str(counter) + ".mp4'\n")
        counter += 1

#Combine all videos into one video
videoList.flush()
os.popen("ffmpeg -f concat -safe 0 -i generate/videos.txt -c copy " + str({args.output})).read()
time.sleep(1)
if os.path.isdir('generate'):
    shutil.rmtree('generate')
os.system('docker kill gentle')
os.system('docker rm gentle')
