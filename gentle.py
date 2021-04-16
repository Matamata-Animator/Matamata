import os
import requests
import colorama

import docker

from typing import Union

try:
    client: docker.Client = docker.from_env()
except docker.errors.DockerException:
    raise Exception('Make sure Docker Desktop is running')


def init() -> docker.DockerClient.containers:
    container = client.containers.run('lowerquality/gentle', ports={'8765/tcp': 8765}, detach=True, name='gentle')

    # wait until image is running
    while container.status != 'created':
        pass
    return container


def terminate(container: Union[docker.DockerClient.containers, str]) -> None:
    if type(container) == type(docker.DockerClient.containers):
        container.kill()
        container.remove()
    if (type(container) == 'str'):
        for c in client.containers.list():
            if c.name == 'gentle':
                c.kill()
                c.remove()


def align(audio, text) -> dict:
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
