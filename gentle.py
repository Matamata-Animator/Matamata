import command
import subprocess
import json
import os


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
    print(f'curl -F "audio=@{audio}"  -F "transcript=@{text}" "http://localhost:8765/transcriptions?async=false"')
    res = os.popen(
        f'curl -F "audio=@{audio}"  -F "transcript=@{text}" "http://localhost:8765/transcriptions?async=false"').read()

    gentle_out = clean(json.loads(res))

    print(gentle_out)
    return gentle_out
