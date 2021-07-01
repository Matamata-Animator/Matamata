import os
import requests
import colorama

import docker

from typing import Union

import time

try:
    client: docker.DockerClient = docker.from_env()
except docker.errors.DockerException:
    raise Exception('Make sure Docker Desktop is running')


def init(name: str, port: int) -> docker.DockerClient.containers:
    container = client.containers.run('lowerquality/gentle', ports={f'{port}/tcp': port}, detach=True, name=name)

    # wait until image is running
    while container.status != 'created':
        pass
    while not is_ready(port):
        time.sleep(1)

    return container


def is_ready(port: int) -> bool:
    url = f'http://localhost:{port}'
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return r.status_code == 200


def terminate(container: Union[type(docker.DockerClient.containers), str], name) -> None:
    if isinstance(container, type(docker.DockerClient.containers)):
        container.kill()
        container.remove()
    if isinstance(container, str):
        for c in client.containers.list():
            if c.name == name:
                c.kill()
                c.remove()


def align(audio, text, port) -> dict:
    colorama.init(convert=True)
    while not os.path.isfile(audio):
        pass
    while not os.path.isfile(text):
        pass

    # get output from gentle
    url = f'http://localhost:{port}/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open('generate/script.txt', 'rb')}
    try:
        r = requests.post(url, files=files)
    except requests.exceptions.RequestException as e:
        raise Exception(
            colorama.Fore.RED + '[ERR 503] Failed to post to Gentle: Make sure Docker Desktop is running...')

    return r.json()
