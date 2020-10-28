from PIL import Image
import sys
import cv2 as cv
import numpy as np
import time
from subprocess import Popen
import os
import json

docker = Popen(['docker', 'run', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(1)
r = os.popen('curl -F "audio=@pangram-1.mp3" -F "transcript=@pangram-1.txt" "http://localhost:8765/transcriptions?async=false"').read()
phoneReferance = json.load(open('phonemes.json', encoding='utf8'))
characters = json.load(open('characters.json', encoding='utf8'))

stamps = json.loads(r)
for w in range(len(stamps['words'])):
    word = stamps['words'][w]
    for p in range(len(word['phones'])):
        phone = (word['phones'][p]['phone'])
