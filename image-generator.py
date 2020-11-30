import time
import subprocess
import os
import json
from PIL import Image
import sys
import cv2 as cv
import numpy as np
import shutil
import argparse
import random
from tqdm.auto import tqdm
from colorama import Fore, Back, Style

#Arg Parse Stuff
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--audio', required=True, type=str)
parser.add_argument('-t', '--text', required=True, type=str)
parser.add_argument('-o', '--output', required=False, default='output.mov', type=str)
parser.add_argument('-s', '--offset', required=False, default='0.25', type=float)

parser.add_argument('-c', '--character', required=False, default='characters.json', type=str)
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add_argument('-d', '--scale', required=False, default='1920:1080', type=str)

parser.add_argument('-v', '--verbose', required=False, default=False, type=bool)

parser.add_argument('-r', '--framerate', required=False, default=25, type=int)


parser.add_argument('-l', '--skipframes', required=False, type=bool, default=True)
parser.add_argument('-T', '--skipthreshold', required=False, type=float, default=1)
args = parser.parse_args()



banner = '''
                _          _      _          _____
     /m        | |        | |    (_)        / ____|
    /  m  _   _| |_ ___   | |     _ _ __   | (___  _   _ _ __   ___
   / /m m| | | | __/ _ m  | |    | | '_ m   m___ m| | | | '_ m / __|
  / ____ m |_| | || (_) | | |____| | |_) |  ____) | |_| | | | | (__
 /_/    m_m__,_|m__m___/  |______|_| .__/  |_____/ m__, |_| |_|m___|
                                   | |              __/ |
                                   |_|             |___/
'''
print(Fore.GREEN + banner.replace('m', '\\') + Style.RESET_ALL)
def runCommand(command, sync=True):
    command = command.split(' ')
    out = ''
    if(sync):
        process = subprocess.run(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=False)
        out = process

    else:
        process = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()
        out, err = process.communicate()
        if(err != ''):
            print(Fore.RED + "REEEEE")
            print(Fore.RED + err)
    # out = str(out, "utf-8")
    if(args.verbose):
        print(out)
    return out


if os.path.isdir('generate'):
    shutil.rmtree('generate')

command = runCommand('docker kill gentle')


command = runCommand('docker rm gentle')

os.mkdir('generate')

docker = subprocess.Popen(['docker', 'run','--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(3)
videoList = open('generate/videos.txt', 'w+')






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
            poses[numPoses] = startCharacter
        elif i == endCharacter:
            recording = False
            poses[numPoses] += endCharacter
            numPoses += 1
        else:
            if recording:
                poses[numPoses] += i

    #remove extra empty array entry
    del poses[-1]

    #remove tags from script
    for pose in poses:
        text = text.replace(pose, "¦")
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

def getFacePath(pose, characters):
    splitPose = pose.split('-')
    posesList = characters[splitPose[0]] #splits to remove directional tag
    pose = posesList[min(random.randint(0, len(posesList)), len(posesList)-1)]

    #determain wherther to flip image
    mirrorPose = False
    mirrorMouth = False
    lookingLeft = True
    if(len(splitPose) == 2):
        if(splitPose[1].lower() == 'right' or splitPose[1].lower() == 'r'):
            lookingLeft = False
        if(lookingLeft != pose['facingLeft']):
            mirrorPose = True
    if(not pose["facingLeft"]):
            mirrorMouth = True
    return {
        'facePath': characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': characters['default_scale'] * pose['scale'],
        'mirror': [mirrorPose, mirrorMouth]
        }

def createVideo(name, fPath, mPath, mScale, xPos, yPos, time, frame, totalTime, mirror, syl):
    skip = True
    if not args.skipframes or syl == 1 or (time >= args.skipthreshold/args.framerate):
        skip = False

    if (not skip):
        time = round(time * args.framerate)/args.framerate
        time = max(1/args.framerate, time)
        totalTime += time
        image = cv.imread(fPath, 0)
        face =  Image.open(fPath).convert("RGBA")
        mouth = Image.open(mPath).convert("RGBA")
        mouth = mouth.resize([int(mouth.size[0] * mScale), int(mouth.size[1] * mScale)])


        width = image.shape[1]
        height = image.shape[0]
        mouthPos = [xPos, yPos]
        if(mirror[1]):
            mouth = mouth.transpose(Image.FLIP_LEFT_RIGHT)
        face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)

        if(mirror[0]):
            face = face.transpose(Image.FLIP_LEFT_RIGHT)


        face.save("generate/" + str(frame) + '.png')
        # os.popen("ffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(time) + " -pix_fmt yuv420p -vf scale=" + str(args.scale) + " generate/" + str(frame) + ".mp4")
        runCommand("ffmpeg -loop 1 -i generate/" + str(frame) + ".png -c:v libx264 -t " + str(time) + " -pix_fmt yuv420p -r " + str(args.framerate) + " -vf scale=" + str(args.scale) + " generate/" + str(frame) + ".mp4")
        videoList.write("file '" + str(frame) + ".mp4'\n")
    return [totalTime, frame + 1]



def main():
    phoneReference = json.load(open(str(args.mouths), encoding='utf8'))
    charactersJSON = json.load(open(str(args.character), encoding='utf8'))


    #Counters:
    totalTime = 0 #totalTime keeps a running total of how long the animation is at any given point.
    frameCounter = 0 #keeps tracke of which frame is currently bein animated
    poseCounter = 0 #keeps track of which pose is currently being animated
    markedCounter = 0 #keeps track of which word in the script is being read

    #Remove and residual folders and procesees from last time the program was run.

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
    if(args.verbose):
        print(posesList)

    #get output from gentle
    r = os.popen('curl -F "audio=@' + (args.audio) +'" -F "transcript=@' + feederScript + '" "http://localhost:8765/transcriptions?async=false"').read()
    # r = runCommand('curl -F "audio=@' + (args.audio) +'" -F "transcript=@' + feederScript + '" "http://localhost:8765/transcriptions?async=false"')

    stamps = json.loads(r)





    #Make mouth closed until first phoname
    pose = getFacePath(posesList[poseCounter][1:-1], charactersJSON)

    facePath = pose['facePath']
    face =  Image.open(facePath).convert("RGBA")

    mouthPath = phoneReference['mouthsPath'] + phoneReference['closed']

    totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], round(stamps['words'][0]['start'], 4) - float(args.offset), frameCounter, totalTime, pose['mirror'], 1)

    markedCounter += 1 #Increase by 1 to get past the initial pose marker
    poseCounter += 1
    for w in tqdm(range(len(stamps['words']))):
        if markedScript[markedCounter] == '¦':
            pose = getFacePath(posesList[poseCounter][1:-1], charactersJSON)

            facePath = pose['facePath']
            face =  Image.open(facePath).convert("RGBA")

            markedCounter += 1
            poseCounter += 1



        word = stamps['words'][w]
        wordTime = 0
        try:
            for p in range(len(word['phones'])):
                #Identify current phone
                phone = (word['phones'][p]['phone']).split('_')[0]
                wordTime += word['phones'][p]['duration']
                #Referance phonemes.json to see which mouth goes with which phone
                mouthPath = "mouths/" + (phoneReference['phonemes'][phone]['image'])




                totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], word['phones'][p]['duration'], frameCounter, totalTime, pose['mirror'], p)
        except:

            mouthPath = "mouths/" + (phoneReference['phonemes']['aa']['image'])




            totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1],  round(stamps['words'][w-1]['end'], 4) - round(stamps['words'][w + 1]['start'], 4) - 2/args.framerate, frameCounter, totalTime, pose['mirror'], p)
        if (w < len(stamps['words']) - 1):
            mouthPath = phoneReference['mouthsPath'] + 'closed.png'
            # mouth = Image.open(mouthPath).convert("RGBA")
            if(stamps['words'][w + 1]['case'] == 'success'):
                totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], round(stamps['words'][w + 1]['start'], 4) - totalTime - float(args.offset), frameCounter, totalTime, pose['mirror'], 1)
            else:
                totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], 0, frameCounter, totalTime, pose['mirror'], 1)


        markedCounter += 1
        print(" ", end='\r')
    mouthPath = phoneReference['mouthsPath'] + phoneReference['closed']
    totalTime, frameCounter = createVideo(frameCounter, facePath, mouthPath, pose['scale'], pose['mouthPos'][0], pose['mouthPos'][1], args.skipthreshold/args.framerate, frameCounter, totalTime, pose['mirror'], 1)




    #Combine all videos into one video
    videoList.flush()
    videoList.close()

    #delete old output files
    if os.path.isfile(str(args.output)):
        os.remove(str(args.output))

    print("Finishing Up...")

    runCommand("ffmpeg -i " + str(args.audio) + " -f concat -safe 0 -i generate/videos.txt -c copy " + str(args.output))

    #delete all generate files
    # if os.path.isdir('generate'):
    #     shutil.rmtree('generate')
    runCommand('docker kill gentle')
    runCommand('docker rm gentle')
if __name__ == '__main__':
    main()
    print(Style.RESET_ALL + 'done')
