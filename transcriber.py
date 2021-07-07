from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
from pydub import AudioSegment

import json


def transcribe(file_name):
    """
    Transcribe audio into text

    :param str file_name: Path to wav file
    :return str: Transcribed text
    """

    sound = AudioSegment.from_wav(file_name)
    sound = sound.set_channels(1)
    sound.export("generate/audio.wav", format="wav")

    SetLogLevel(-1)

    if not os.path.exists("model"):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)

    wf = wave.open('generate/audio.wav', "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
            # print(rec.Result())
        else:
            pass
            # print(rec.PartialResult())

    r = rec.FinalResult()
    r = json.loads(r)
    return r['text']


def create_script(file_name, out='generated_script.txt'):
    """
    Writa transcribe audio to a file

    :param str file_name: Path to wav file
    :param str out: Path to output transcribe file
    :return None:
    """
    script = open(out, 'w+')
    text = transcribe(file_name)
    script.write(text)
