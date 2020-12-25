import command
import subprocess
import json
import os


def init():
    command.run('docker kill gentle')

    command.run('docker rm gentle')
    docker = subprocess.Popen(['docker', 'run', '--name', 'gentle', '-p', '8765:8765', 'lowerquality/gentle'], shell=True)


def align(audio, text):
    # get output from gentle
    res = os.popen(
        f'curl -F "audio=@{audio}"  -F "transcript=@{text}" "http://localhost:8765/transcriptions?async=false"').read()

    gentle_out = json.loads(res)
    return gentle_out
