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
        # if args.verbose:
        if True:
            print(f'({silence[i][1]}, {silence[i + 1][0]})')
        start = (silence[i][1] - 0.5) * 1000
        end = (silence[i + 1][0] + 0.5) * 1000
        speak = audio[start:end]
        speak.export(f'generate/audio/{i}.wav', 'wav')


def find_blocks():
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
    text = stamps['words'][0]['word'] + ' '
    block_start = 0
    blocks = []
    for word in range(len(stamps['words'])):
        if word != 0:
            base_word_gap = 0.5
            word_gap = base_word_gap
            word_add = 0
            word_subtract = 1

            while 'start' not in stamps['words'][word + word_add]:
                word_gap += base_word_gap
                word_add += 1
            while 'end' not in stamps['words'][word - word_subtract]:
                word_gap += base_word_gap
                word_subtract += 1

            if stamps['words'][word + word_add]['start'] - stamps['words'][word - word_subtract]['end'] > word_gap:
                block_end = word
                blocks.append((block_start, block_end))
                block_start = word + 1
            elif stamps['words'][word] == stamps['words'][-1]:
                block_end = word
                blocks.append((block_start, block_end))
    return blocks, parsed_script['pose_markers_script']


def make_scripts(blocks, script):
    script = script.split(' ')
    print(script)

    word_counter = 0
    spoken_word_counter = 0
    for block in range(len(blocks)):
        text = ''
        while spoken_word_counter < blocks[block][1]:
            text += script[word_counter] + ' '

            if script[word_counter] != '¦':
                spoken_word_counter += 1
            word_counter += 1

        blocked_script = open(f'generate/scripts/{block}.txt', 'w+')
        blocked_script.write(text)
        blocked_script.flush()
        blocked_script.close()



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
    os.makedirs('generate/scripts')
    while not os.path.isdir('generate/audio'):
        pass

    split_audio()
    script_blocks = find_blocks()
    make_scripts(script_blocks[0], script_blocks[1])

    ig.gen_vid(args)
    # delete all generate files
    while not os.path.isfile(args.output):
        pass
    # shutil.rmtree('generate')
    print(Style.RESET_ALL + 'done')
