from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
from pydub import AudioSegment

import json


def transcribe(file_name, model_dir, gen_dir='generate'):
    """
    Transcribe audio into text
    :param str file_name: Path to wav file
    :return str: Transcribed text
    """

    sound = AudioSegment.from_wav(file_name)
    sound = sound.set_channels(1)
    sound.export(f'{gen_dir}/audio.wav', format="wav")

    SetLogLevel(-1)

    if not os.path.exists(model_dir):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)

    wf = wave.open(f'{gen_dir}/audio.wav', "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())

    rec.SetWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
        else:
            pass

    r = rec.FinalResult()
    r = json.loads(r)
    return r


if __name__ == '__main__':
    j = json.dumps(transcribe(sys.argv[1], sys.argv[2]))
    print(j)
