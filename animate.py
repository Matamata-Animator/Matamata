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

# Arguments
parser.add_argument('-a', '--audio', required=True, type=str)
parser.add_argument('-t', '--text', required=True, type=str)
parser.add_argument('-o', '--output', required=False, default='output.mov', type=str)
parser.add_argument('-s', '--offset', required=False, default='0.25', type=float)

parser.add_argument('-c', '--character', required=False, default='characters.json', type=str)
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add_argument('-d', '--scale', required=False, default='1920:1080', type=str)

parser.add_argument('-r', '--framerate', required=False, default=100, type=int)

parser.add_argument('-T', '--skip_thresh', required=False, type=float, default=1)

parser.add_argument('-q', '--silence_thresh', required=False, default=-40, type=float)
parser.add_argument('-w', '--silence_len', required=False, default=1000, type=int)

# Flags
parser.add_argument('--no_delete', required=False, default=False, action='store_true')
parser.add_argument('-v', '--verbose', required=False, default=False, action='store_true')
parser.add_argument('--skip_frames', required=False, default=False, action='store_true')
parser.add_argument('--crumple_zone', required=False, default=False, action='store_true')

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

    os.makedirs('generate/images')
    os.makedirs('generate/videos')
    while not os.path.isdir('generate/videos'):
        pass


def shutdown():
    # delete all generate files
    while not os.path.isfile(args.output):
        pass
    if not args.no_delete:
        shutil.rmtree('generate')

    command.run('docker kill gentle')
    command.run('docker rm gentle')
    colorama.init(convert=True)
    print(f'{Style.RESET_ALL}Done')

    # delete old output files
    if os.path.isfile(args.output):
        os.remove(args.output)
    print('\nFinishing Up...')

    if args.crumple_zone:
        make_crumple(len(script_blocks['blocks']))

    command.run(
        f'ffmpeg -f concat -safe 0 -i generate/videos/videos.txt -c copy {args.output} -r {args.framerate}')


def num_phonemes(gentle):
    gentle = gentle['gentle']
    phones = len(gentle['words'])
    for word in gentle['words']:
        if word['case'] == 'success':
            phones += len(word['phones'])
    return phones


def make_crumple(name):
    vid_name = f'{name}.{args.output.split(".")[-1]}'
    last_list = open(f'generate/{name - 1}/videos.txt', 'r').read().split('\n')
    last_img = last_list[-2].split(' ')[1].split('.')[0]

    command.run(
        f'ffmpeg -loop 1 -i generate/{name - 1}/{last_img}.png -c:v libx264 -t {args.framerate / 20} -pix_fmt yuv420p -r {args.framerate} -vf scale={args.scale} generate/videos/{vid_name}')
    videos_list = open('generate/videos/videos.txt', 'a')
    videos_list.write(f'file {vid_name}\n')
    videos_list.flush()
    videos_list.close()


def find_poses():
    # Parse script, output parsed script to generate
    raw_script = open(args.text, 'r').read()
    parsed_script = parse_script(raw_script)
    feeder_script = 'generate/script.txt'
    script_file = open(feeder_script, 'w+')
    script_file.write(parsed_script['feeder_script'])
    script_file.flush()
    script_file.close()

    marked_text = ' '.join(parsed_script['marked_text'])
    # marked_script_path = 'generate/marked_script.txt'
    # script_file = open(marked_script_path, 'w+')
    # script_file.write(marked_text)
    # script_file.flush()
    # script_file.close()

    poses_loc = []
    for word in range(len(parsed_script['marked_text'])):
        if parsed_script['marked_text'][word] == '¦':
            poses_loc.append(word)
    print(poses_loc)
    return {
        'poses_loc': poses_loc,
        'script': parsed_script['pose_markers_script'],
        'poses_list': parsed_script['poses_list'],
        'marked_script': parsed_script['marked_text']
    }


if __name__ == '__main__':
    init()

    # Generate the feeder script, get poses list, and where each pose should go in the script.
    print('Analyzing Text...')
    script_blocks = find_poses()
    poses_list = script_blocks['poses_list']
    pose_counter = 0

    # Get gentle out
    stamps = gentle.align(args.audio, 'generate/script.txt')
    num_names = num_phonemes(stamps)
    ig.init(num_names)

    req_vid: ig.VideoRequest = args
    req_vid.poses_list = poses_list
    req_vid.poses_loc = script_blocks['poses_loc']


    print("reeeeeeeeeeeeeeeeeeeeee")
    ig.gen_vid(args)
    # ig.progress_bar(script_blocks['num_phonemes'])
    quit()
    shutdown()
