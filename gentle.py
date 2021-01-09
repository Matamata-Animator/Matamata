import command
import os
import requests
import colorama


def init():
    command.run('docker kill gentle')

    command.run('docker rm gentle')
    command.run('docker run --name gentle -p 8765:8765 lowerquality/gentle', False)
    #wait until imafge is running
    while 'lowerquality/gentle' not in command.run('docker ps'):
        pass

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
        raise Exception(colorama.Fore.RED + '[ERR 503] Failed to post to Gentle: Make sure Docker Desktop is running...')



    return r.json()
