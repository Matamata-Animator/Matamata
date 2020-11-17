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
import random




#Arg Parse Stuff
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--audio', required=True)
parser.add_argument('-t', '--text', required=True)
parser.add_argument('-o', '--output', required=False, default='output.mp4')
parser.add_argument('-s', '--offset', required=False, default='0.8')

parser.add_argument('-c', '--character', required=False, default='characters.json')
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json')

parser.add_argument('-d', '--scale', required=False, default='1920:1080')


args = parser.parse_args()



phoneReference = json.load(open(str(args.mouths), encoding='utf8'))
charactersJSON = json.load(open(str(args.character), encoding='utf8'))


#Counters:
totalTime = 0 #totalTime keeps a running total of how long the animation is at any given point.
frameCounter = 0 #keeps tracke of which frame is currently bein animated
poseCounter = 0 #keeps track of which pose is currently being animated
markedCounter = 0 #keeps track of which word in the script is being read



#Remove and residual folders and procesees from last time the program was run.
if os.path.isdir('generate'):
    shutil.rmtree('generate')
os.system('docker kill gentle')
os.system('docker rm gentle')
os.mkdir('generate')

#The delays gives gentle proper time to launch.
time.sleep(1)
docker = Popen(['docker', 'run','--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(3)





def parseScript(text, startCharacter='[', endCharacter=']'): #Parse script to identify pose tags. strart/endCharacter are by default set to brackets []
    startCharacter = startCharacter[0]
    endCharacter = endCharacter[0]
    poses = [""]
    recording = False
    numPoses = 0
    for i in text:
        if i == startCharacter and not recording:
            recording = True
            poses.append("")
        elif i == endCharacter:
            recording = False
            numPoses += 1
        else:
            if recording:
                poses[numPoses] += i

    #remove extra empty array entry
    del poses[-1]

    #remove tags from script
    for pose in poses:
        text = text.replace(startCharacter + pose + endCharacter, "¦")
    feederScript = text.replace("¦", " ")

    #create a list of words
    markedText = text.replace('\n', ' ')
    markedText = ' '.join(markedText.split())
    markedText = markedText.split(' ')
    return { # Out puts a dictionary with the list of poses, the script with markers of where
        'posesList': poses,
        'markedText': markedText,
        'feederScript': text.replace("¦", " ")
        }
def getFacePath(pose, characters=charactersJSON):
    posesList = characters[pose]
    pose = posesList[min(random.randint(0, len(posesList)), len(posesList)-1)]
    return {
        'facePath': characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': characters['default_scale'] * pose['scale']
        }

def createVideo(fPath, mPath, mScale, xPos, yPos, time, frame):
    global totalTime
    time = max(0.001, time)
    totalTime += time
    image = cv.imread(fPath, 0)
    face =  Image.open(fPath).convert("RGBA")
    mouth = Image.open(mPath).convert("RGBA")
    mouth = mouth.resize([int(mouth.size[0] * mScale), int(mouth.size[1] * mScale)])


    width = image.shape[1]
    height = image.shape[0]
    mouthPos = [xPos, yPos]
    face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
    face.save("generate/" + str(frameCounter) + '.png')
    os.popen("ffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(time) + " -pix_fmt yuv420p -vf scale=" + str(args.scale) + " generate/" + str(frame) + ".mp4")
    videoList.write("file '" + str(frame) + ".mp4'\n")
    return frame + 1



#Parse script, output parsed script to generate
rawScript = open(args.text, 'r').read()
parsedScript = parseScript(rawScript)
feederScript = 'generate/script.txt'
scriptFile = open(feederScript, 'w+')
scriptFile.write(parsedScript['feederScript'])
scriptFile.flush()
scriptFile.close()
posesList = parsedScript['posesList']
markedScript = parsedScript['markedText']
print(markedScript)




#get output from gentle
r = os.popen('curl -F "audio=@' + (args.audio) +'" -F "transcript=@' + feederScript + '" "http://localhost:8765/transcriptions?async=false"').read()


stamps = json.loads(r)
videoList = open('generate/videos.txt', 'w+')





#Make mouth closed until first phoname
pose = getFacePath(posesList[poseCounter])
facePath = pose['facePath']
face =  Image.open(facePath).convert("RGBA")

mouthPath = phoneReference['mouthsPath'] + phoneReference['closed']

frameCounter = createVideo(facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], round(stamps['words'][0]['start'], 4) - float(args.offset), frameCounter)

markedCounter += 1 #Increase by 1 to get past the initial pose marker
poseCounter += 1
for w in range(len(stamps['words'])):
    if markedScript[markedCounter] == '¦':
        pose = getFacePath(posesList[poseCounter])
        facePath = pose['facePath']
        face =  Image.open(facePath).convert("RGBA")

        markedCounter += 1
        poseCounter += 1



    word = stamps['words'][w]
    print(word['alignedWord'])
    wordTime = 0
    for p in range(len(word['phones'])):
        #Identify current phone
        phone = (word['phones'][p]['phone']).split('_')[0]
        wordTime += word['phones'][p]['duration']
        #Referance phonemes.json to see which mouth goes with which phone
        mouthPath = "mouths/" + (phoneReference['phonemes'][phone]['image'])




        frameCounter = createVideo(facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], word['phones'][p]['duration'], frameCounter)
    if (w < len(stamps['words']) - 1):
        mouthPath = phoneReference['mouthsPath'] + 'closed.png'
        # mouth = Image.open(mouthPath).convert("RGBA")
        frameCounter = createVideo(facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], round(stamps['words'][w + 1]['start'], 4) - totalTime - float(args.offset), frameCounter)


    markedCounter += 1




#Combine all videos into one video
videoList.flush()
videoList.close()

#delete old output files
if os.path.isfile(str(args.output)):
    os.remove(str(args.output))



os.popen("ffmpeg -i " + str(args.audio) + " -f concat -safe 0 -i generate/videos.txt -c copy " + str(args.output)).read()
time.sleep(1)

#delete all generate files
if os.path.isdir('generate'):
    shutil.rmtree('generate')
os.system('docker kill gentle')
os.system('docker rm gentle')
