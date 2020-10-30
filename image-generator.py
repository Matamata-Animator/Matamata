import time
from subprocess import Popen
import os
import json
from PIL import Image
import sys
import cv2 as cv
import numpy as np






os.system('docker kill gentle')
os.system('docker rm gentle')
time.sleep(1)
docker = Popen(['docker', 'run','--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(1)
r = os.popen('curl -F "audio=@test-audio-1.mp3" -F "transcript=@test-audio-1.txt" "http://localhost:8765/transcriptions?async=false"').read()
phoneReference = json.load(open('phonemes.json', encoding='utf8'))
characters = json.load(open('characters.json', encoding='utf8'))

facePath = "faces/dumb-smile.png"
mouthPath = 'mouths/closed.png'

stamps = json.loads(r)
counter = 0
videoList = open('generate/videos.txt', 'w+')
numW = 0
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
        width = image.shape[1]
        height = image.shape[0]
        mouthPos = [characters['stupid'][0]['x'], characters['stupid'][0]['y']]

        #convert faace and mouth images to RGBA
        face =  Image.open(facePath).convert("RGBA")
        mouth = Image.open(mouthPath).convert("RGBA")

        #Place mouth over the mouth location speccified in chatacters.json
        mouth = mouth.resize((int(mouth.width * characters['default_scale']), int(mouth.height * characters['default_scale'])))
        face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)

        #Save as image
        face.save("generate/" + str(counter) + '.png')


        cv.waitKey(0)
        cv.destroyAllWindows()

        #Convert image to a video
        os.popen("ffmpeg -loop 1 -i generate/" + str(counter) + ".png -c:v libx264 -t " + str(word['phones'][p]['duration']) + " -pix_fmt yuv420p -vf scale=1920:1080 generate/" + str(counter) + ".mp4")
        videoList.write("file '" + str(counter) + ".mp4'\n")

        #increase image counter
        counter += 1
    if (w < len(stamps['words']) -1):
        numW = counter
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
    #
        counter += 1
    #     cv.waitKey(0)
    #     cv.destroyAllWindows()

#Combine all videos into one video
videoList.flush()
time.sleep(3)

os.popen("ffmpeg -f concat -safe 0 -i generate/videos.txt -c copy output.mp4").read()
print(stamps['words'][w]['endOffset']/100)
