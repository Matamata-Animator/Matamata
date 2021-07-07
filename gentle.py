import os
import requests
import colorama

import docker

try:
    client: docker.DockerClient = docker.from_env()
except docker.errors.DockerException:
    raise Exception('Make sure Docker Desktop is running')


def init(tag: str, name: str, port: int) -> docker.DockerClient.containers:
    """
    Launch docker container

    ":param tag:
    :param name:
    :param port:
    :return:
    """
    container = client.containers.run(tag, ports={f'{port}/tcp': port}, detach=True, name=name)

    # wait until image is running
    while container.status != 'created':
        pass

    return container


def is_ready(port: int) -> bool:
    """
    Check to see if gentle is ready for usage

    :param port: Port gentle is running on
    :return bool:
    """
    url = f'http://localhost:{port}'
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return r.status_code == 200


def terminate(container: type(docker.DockerClient.containers)) -> None:
    """
    Kill and remove a live docker container

    :param container: Docker container
    :return None:
    """
    container.kill()
    container.remove()


def remove_old(name):
    """
    Kill and remove a docker container by name

    :param str name: Container name
    :return None:
   """
    for c in client.containers.list(all=True):
        if c.name == name:
            if c.status != 'exited':
                c.kill()
            c.remove()


def align(audio, text, port=8765) -> dict:
    """
    Get aligned gentle output

    :param audio: Path to audio
    :param text: Path to text transcript
    :param port: Port of gentle (default=8765)
    :return dict: JSON phonemes and timestamps
    """
    colorama.init(convert=True)
    while not os.path.isfile(audio):
        pass
    while not os.path.isfile(text):
        pass

    # get output from gentle
    url = f'http://localhost:{port}/transcriptions?async=false'
    files = {'audio': open(audio, 'rb'),
             'transcript': open(text, 'rb')}
    try:
        r = requests.post(url, files=files)
    except requests.exceptions.RequestException as e:
        raise Exception(
            colorama.Fore.RED + '[ERR 503] Failed to post to Gentle: Make sure Docker Desktop is running...')

    return r.json()

