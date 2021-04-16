import os
import requests
import colorama

import docker


def init() -> docker.DockerClient.containers:
    client: docker.Client = docker.from_env()
    for c in client.containers.list():
        if c.name == 'gentle':
            c.kill()
            c.remove()
    container = client.containers.run('lowerquality/gentle', ports={'8765/tcp': 8765}, detach=True, name='gentle')

    # wait until image is running
    while container.status != 'created':
        pass
    return container


def align(audio, text):
    colorama.init(convert=True)
    while not os.path.isfile(audio):
        pass
    while not os.path.isfile(text):
        pass

    # get output from gentle
    url = 'http://localhost:8765/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open('generate/script.txt', 'rb')}
    try:
        r = requests.post(url, files=files)
    except requests.exceptions.RequestException as e:
        raise Exception(
            colorama.Fore.RED + '[ERR 503] Failed to post to Gentle: Make sure Docker Desktop is running...')

    return r.json()
