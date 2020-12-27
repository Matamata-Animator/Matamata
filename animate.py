# python animate.py -a intro2.output.wav -t ree


import argparse
from colorama import Fore, Back, Style
import image_generator as ig
import os
import time
import shutil
import gentle

import pydub

# Arg Parse Stuff
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--audio', required=True, type=str)
parser.add_argument('-t', '--text', required=True, type=str)
parser.add_argument('-o', '--output', required=False, default='output.mov', type=str)
parser.add_argument('-s', '--offset', required=False, default='0.25', type=float)

parser.add_argument('-c', '--character', required=False, default='characters.json', type=str)
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add_argument('-d', '--scale', required=False, default='1920:1080', type=str)

parser.add_argument('-v', '--verbose', required=False, default=False, type=bool)

parser.add_argument('-r', '--framerate', required=False, default=25, type=int)

parser.add_argument('-l', '--skip_frames', required=False, type=bool, default=True)
parser.add_argument('-T', '--skip_thresh', required=False, type=float, default=1)

parser.add_argument('-q', '--silence_thresh', required=False, default=-40, type=float)

args = parser.parse_args()

banner = '''
                _          _      _          _____
     /m        | |        | |    (_)        / ____|
    /  m  _   _| |_ ___   | |     _ _ __   | (___  _   _ _ __   ___
   / /m m| | | | __/ _ m  | |    | | '_ m   m___ m| | | | '_ m / __|
  / ____ m |_| | || (_) | | |____| | |_) |  ____) | |_| | | | | (__
 /_/    m_m__,_|m__m___/  |______|_| .__/  |_____/ m__, |_| |_|m___|
                                   | |              __/ |
                                   |_|             |___/
'''


def split_audio():
    audio = pydub.AudioSegment.from_file("intro2.output.wav..")
    # audio = audio.reverse()
    silence = pydub.silence.detect_silence(audio, silence_thresh=args.silence_thresh)
    silence = [((start / 1000), (stop / 1000)) for start, stop in silence]  # convert to sec
    silence.append((len(audio), len(audio)))
    for i in range(len(silence) - 1):
        print(f'({silence[i][1]}, {silence[i + 1][0]})')
        start = (silence[i][1] - 0.5) * 1000
        end = (silence[i + 1][0] + 0.5) * 1000
        speak = audio[start:end]
        speak.export(f'generate/audio/{i}.wav', 'wav')


if __name__ == '__main__':
    print(Fore.GREEN + banner.replace('m', '\\') + Style.RESET_ALL)
    if os.path.isdir('generate'):
        shutil.rmtree('generate')
    gentle.init()
    time.sleep(3)
    os.mkdir('generate')
    os.mkdir('generate/audio')

    time.sleep(3)
    # split_audio()

    ig.gen_vid(args)
    print(Style.RESET_ALL + 'done')
