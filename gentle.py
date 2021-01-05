import command
import json
import pycurl
from io import BytesIO
import os
import requests


def init():
    command.run('docker kill gentle')

    command.run('docker rm gentle')
    # command.run('docker run --name gentle -p 8765:8765 lowerquality/gentle', False)


def clean(gentle):
    while gentle['words'][0]['case'] == 'not-found-in-audio':
        del gentle['words'][0]
    while gentle['words'][-1]['case'] == 'not-found-in-audio':
        del gentle['words'][-1]
    return gentle


def align(audio, text):
    while not os.path.isfile(audio):
        pass
    while not os.path.isfile(text):
        pass

    # # get output from gentle
    print('reeeeeeee')

    url = 'http://localhost:8765/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open('generate/script.txt', 'rb')}
    r = requests.post(url, files=files)
    gentle_out = json.loads(r)
    return gentle_out
