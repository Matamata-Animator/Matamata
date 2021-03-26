from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
from pydub import AudioSegment

import json


def transcribe(file_name):
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


def create_script(file_name):
    script = open('generated_script.txt', 'w+')
    text = transcribe(file_name)
    script.write(text)


if __name__ == '__main__':
    print(transcribe('custom/test.wav'))
