import time
from subprocess import Popen
import os
import json
from PIL import Image
import sys
import cv2 as cv
import numpy as np
from moviepy.editor import *

os.system('docker kill gentle')
os.system('docker rm gentle')
time.sleep(1)
docker = Popen(['docker', 'run','--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(1)
r = os.popen('curl -F "audio=@pangram-1.mp3" -F "transcript=@pangram-1.txt" "http://localhost:8765/transcriptions?async=false"').read()
phoneReference = json.load(open('phonemes.json', encoding='utf8'))
characters = json.load(open('characters.json', encoding='utf8'))

stamps = json.loads(r)
counter = 0
videoList = open('generate/videos.txt', 'w+')
for w in range(len(stamps['words'])):
    word = stamps['words'][w]
    print(word['alignedWord'])
    for p in range(len(word['phones'])):
        phone = (word['phones'][p]['phone']).split('_')[0]

        mouthPath = "mouths/" + (phoneReference['phonemes'][phone]['image'])
        facePath = "faces/dumb-smile.png"
        image = cv.imread(facePath, 0)
        width = image.shape[1]
        height = image.shape[0]
        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]
        face =  Image.open(facePath).convert("RGBA")
        mouth = Image.open(mouthPath).convert("RGBA")
        mouth = mouth.resize((int(mouth.width * characters['default_scale']), int(mouth.height * characters['default_scale'])))
        face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
        face.save("generate/" + str(counter) + '.png')
        cv.waitKey(0)
        cv.destroyAllWindows()
        os.popen("ffmpeg -loop 1 -i generate/" + str(counter) + ".png -c:v libx264 -t " + str(word['phones'][p]['duration']) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(counter) + ".mp4")
        videoList.write("file '" + str(counter) + ".mp4'\n")
        counter += 1
videoList.flush()
os.popen("ffmpeg -f concat -safe 0 -i generate/videos.txt -c copy output.mp4").read()
