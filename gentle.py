import command
import subprocess
import json
import pycurl
import os
from io import BytesIO


def init():
    command.run('docker kill gentle')

    command.run('docker rm gentle')
    docker = subprocess.Popen(['docker', 'run', '--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'],
                              shell=True)


def clean(gentle):
    word = 0
    while gentle['words'][0]['case'] == 'not-found-in-audio':
        del gentle['words'][0]
    while gentle['words'][-1]['case'] == 'not-found-in-audio':
        del gentle['words'][-1]
    return gentle


def align(audio, text):
    # get output from gentle

    buffer = BytesIO()
    g = pycurl.Curl()
    payload = [('audio', (g.FORM_FILE, audio)), ('transcript', (g.FORM_FILE, text))]
    g.setopt(pycurl.URL, "http://localhost:8765/transcriptions?async=false")
    g.setopt(pycurl.HTTPPOST, payload)
    g.setopt(pycurl.WRITEFUNCTION, buffer.write)
    g.perform()
    g.close()
    res = buffer.getvalue().decode("utf-8")
    buffer.close()
    gentle_out = json.loads(res)
    return gentle_out
