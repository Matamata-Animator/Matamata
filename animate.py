# python animate.py -a intro2.output.wav -t ree


import argparse
from colorama import Fore, Back, Style
import colorama
import os
import shutil
import json
import pydub

import gentle
import image_generator as ig
from parse_script import parse_script
import command

# Arg Parse Stuff
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--audio', required=True, type=str)
parser.add_argument('-t', '--text', required=True, type=str)
parser.add_argument('-o', '--output', required=False, default='output.mov', type=str)
parser.add_argument('-s', '--offset', required=False, default='0.25', type=float)

parser.add_argument('-c', '--character', required=False, default='characters.json', type=str)
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add_argument('-d', '--scale', required=False, default='1920:1080', type=str)

parser.add_argument('-v', '--verbose', required=False, default=False, action='store_true')

parser.add_argument('-r', '--framerate', required=False, default=144, type=int)

parser.add_argument('--skip_frames', required=False, default=False, action='store_true')
parser.add_argument('-T', '--skip_thresh', required=False, type=float, default=1)

parser.add_argument('-q', '--silence_thresh', required=False, default=-40, type=float)
parser.add_argument('-w', '--silence_len', required=False, default=1000, type=int)

parser.add_argument('--no_delete', required=False, default=False, action='store_true')

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


def init():
    # Print banner
    colorama.init(convert=True)
    print(Fore.GREEN)
    print(banner.replace('m', '\\'))
    print(Style.RESET_ALL)

    gentle.init()

    # Delete old folder, then create the new ones
    if os.path.isdir('generate'):
        shutil.rmtree('generate')
    while os.path.isdir('generate'):
        pass

    os.makedirs('generate/audio')
    os.makedirs('generate/marked_scripts')
    os.makedirs('generate/feeder_scripts')
    os.makedirs('generate/videos')
    while not os.path.isdir('generate/audio'):
        pass


def split_audio():
    audio = pydub.AudioSegment.from_file(args.audio)
    # audio = audio.reverse()
    len_of_silence = pydub.AudioSegment.silent(duration=args.silence_len)
    audio = len_of_silence + audio
    silence = pydub.silence.detect_silence(audio, silence_thresh=args.silence_thresh, min_silence_len=args.silence_len)
    silence = [((start / 1000), (stop / 1000)) for start, stop in silence]  # convert to sec
    if not silence:
        speak = audio[0:len(audio)]
        speak.export(f'generate/audio/{0}.wav', 'wav')
    else:
        silence.append((len(audio), len(audio)))
        for i in range(len(silence) - 1):
            if args.verbose:
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
    if args.verbose:
        print(poses_list)

    stamps = gentle.align(args.audio, feeder_script)
    if args.no_delete:
        save_gentle = open('generate/gentle.json', 'w+')
        save_gentle.write(json.dumps(stamps, indent=2))
        save_gentle.flush()
        save_gentle.close()
    block_start = 0
    blocks = []
    for word in range(len(stamps['words'])):
        if word != 0:
            base_word_gap = args.silence_len / 1000
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
    return {
        'blocks': blocks,
        'script': parsed_script['pose_markers_script'],
        'poses_list': parsed_script['poses_list'],
        'marked_script': parsed_script['marked_text'],
        'num_phonemes': num_phonemes(stamps)
    }


def make_scripts(blocks, script):
    script = script.split(' ')

    word_counter = 0
    spoken_word_counter = 0
    for block in range(len(blocks)):
        text = ''
        while spoken_word_counter < blocks[block][1]:
            text += script[word_counter] + ' '

            if script[word_counter] != '¦':
                spoken_word_counter += 1
            word_counter += 1
        if block == blocks[-1]:
            text += script[-1]
        blocked_script = open(f'generate/marked_scripts/{block}.txt', 'w+')
        blocked_script.write(text)
        blocked_script.flush()
        blocked_script.close()

        feeder_script = open(f'generate/feeder_scripts/{block}.txt', 'w+')
        feeder_script.write(text.replace('¦', ''))
        feeder_script.flush()
        feeder_script.close()


def num_phonemes(gentle):
    phones = len(gentle['words'])
    for word in gentle['words']:
        if word['case'] == 'success':
            phones += len(word['phones'])
    return phones


if __name__ == '__main__':
    init()

    # divide the project into smaller projects
    print('Analyzing Audio...')
    split_audio()
    print('Analyzing Text...')
    script_blocks = find_blocks()
    make_scripts(script_blocks['blocks'], script_blocks['script'])
    poses_list = script_blocks['poses_list']
    pose_counter = 0

    ig.init(script_blocks['num_phonemes'])
    videos_list = open('generate/videos/videos.txt', 'w+')
    videos_list.close()
    for block in range(len(script_blocks['blocks'])):
        # load block's script and count the number of poses
        marked_script = open(f'generate/marked_scripts/{block}.txt', 'r').read()
        num_poses = len(marked_script.split('¦')) - 1
        num_poses = max(num_poses, 0)

        # create cropped_poses by cropping poses_list
        cropped_poses = poses_list[pose_counter:pose_counter + num_poses]
        if num_poses == 0:
            cropped_poses = [poses_list[max(0, pose_counter - 1)]]
        pose_counter += num_poses

        args.audio = f'generate/audio/{block}.wav'
        args.text = f'generate/feeder_scripts/{block}.txt'
        ig.gen_vid(args, cropped_poses, script_blocks['marked_script'], block)
    ig.progress_bar(script_blocks['num_phonemes'])

    # delete old output files
    if os.path.isfile(args.output):
        os.remove(args.output)
    print('\nFinishing Up...')

    command.run(
        f'ffmpeg -f concat -safe 0 -i generate/videos/videos.txt -c copy {args.output}')
    # delete all generate files
    while not os.path.isfile(args.output):
        pass
    if not args.no_delete:
        shutil.rmtree('generate')

    command.run('docker kill gentle')
    command.run('docker rm gentle')
    colorama.init(convert=True)
    print(f'{Style.RESET_ALL}Done')
