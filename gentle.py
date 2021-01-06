import command
import json
import pycurl
from io import BytesIO
import os
import requests


def init():
    command.run('docker kill gentle')

    command.run('docker rm gentle')
    command.run('docker run --name gentle -p 8765:8765 lowerquality/gentle', False)


def clean(gentle):
    clipped_before = 0
    clipped_after = 0
    while gentle['words'][clipped_before]['case'] == 'not-found-in-audio':
        clipped_before += 1

    if gentle['words'][-clipped_after]['case'] == 'not-found-in-audio':
        clipped_after +=1
    while gentle['words'][-clipped_after]['case'] == 'not-found-in-audio':
        clipped_after += 1

    return {
        'gentle': gentle,
        'clipped_before': clipped_before,
        'clipped_after': clipped_after
    }


def align(audio, text):
    while not os.path.isfile(audio):
        pass
    while not os.path.isfile(text):
        pass

    # get output from gentle
    url = 'http://localhost:8765/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open('generate/script.txt', 'rb')}
    r = requests.post(url, files=files)
    return clean(r.json())
