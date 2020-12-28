# python animate.py -a intro2.output.wav -t ree


import argparse
from colorama import Fore, Back, Style
import os
import shutil
import json
import pydub

import gentle
import image_generator as ig
from parse_script import parse_script


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
    audio = pydub.AudioSegment.from_file(args.audio)
    # audio = audio.reverse()
    silence = pydub.silence.detect_silence(audio, silence_thresh=args.silence_thresh)
    silence = [((start / 1000), (stop / 1000)) for start, stop in silence]  # convert to sec
    silence.append((len(audio), len(audio)))
    for i in range(len(silence) - 1):
        if args.verbose:
            print(f'({silence[i][1]}, {silence[i + 1][0]})')
        start = (silence[i][1] - 0.5) * 1000
        end = (silence[i + 1][0] + 0.5) * 1000
        speak = audio[start:end]
        speak.export(f'generate/audio/{i}.wav', 'wav')


def split_text():
    # Parse script, output parsed script to generate
    raw_script = open(args.text, 'r').read()
    parsed_script = parse_script(raw_script)
    feeder_script = 'generate/script.txt'
    script_file = open(feeder_script, 'w+')
    script_file.write(parsed_script['feeder_script'])
    script_file.flush()
    script_file.close()
    poses_list = parsed_script['poses_list']
    marked_script = parsed_script['marked_text']
    if args.verbose:
        print(poses_list)
    stamps = gentle.align(args.audio, feeder_script)


if __name__ == '__main__':
    # Print banner
    print(Fore.GREEN + banner.replace('m', '\\') + Style.RESET_ALL)

    gentle.init()

    # Delete old folder, then create the new ones
    if os.path.isdir('generate'):
        shutil.rmtree('generate')
    while os.path.isdir('generate'):
        pass
    os.makedirs('generate/audio')
    while not os.path.isdir('generate/audio'):
        pass

    # split_audio()
    # split_text()

    ig.gen_vid(args)

    print(Style.RESET_ALL + 'done')
