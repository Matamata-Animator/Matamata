import argparse
from colorama import Fore, Style
import colorama
import os
import shutil
import json

import gentle
import image_generator as ig
from parse_script import parse_script
import command
from bar import print_bar

import time
import math

# Arg Parse Stuff
parser = argparse.ArgumentParser()

# Arguments
parser.add_argument('-a', '--audio', required=True, type=str)
parser.add_argument('-t', '--text', required=True, type=str)
parser.add_argument('-o', '--output', required=False, default='output.mov', type=str)
parser.add_argument('-s', '--offset', required=False, default='0.00', type=float)

parser.add_argument('-c', '--character', required=False, default='characters.json', type=str)
parser.add_argument('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add_argument('-d', '--dimensions', required=False, default='1920:1080', type=str)

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


def init() -> None:
    # Print banner
    colorama.init(convert=True)
    print(Fore.GREEN)
    print(banner.replace('m', '\\'))
    print(Style.RESET_ALL)

    print("Booting Gentle...")
    gentle.init()

    # Delete old folder, then create the new ones
    shutil.rmtree('generate', ignore_errors=True)
    while os.path.isdir('generate'):
        shutil.rmtree('generate', ignore_errors=True)
        time.sleep(0.01)
    os.makedirs('generate/images')
    while not os.path.isdir('generate/images'):
        pass


def shutdown() -> None:
    # delete all generate files

    command.run('docker kill gentle')
    command.run('docker rm gentle')

    # delete old output files
    if os.path.isfile(args.output):
        os.remove(args.output)
    print('\nFinishing Up...')

    dimensions = args.dimensions.split(':')
    for a in range(len(dimensions)):
        dimensions[a] = math.ceil(int(dimensions[a]) / 2) * 2

    ffmpeg = f'ffmpeg -r 100 -i generate/images/%d.png -i {args.audio} -vf scale={dimensions[0]}:{dimensions[1]} -c:v libx264 -pix_fmt yuv420p {args.output}'
    command.run(ffmpeg)
    while not os.path.isfile(args.output):
        pass
    if not args.no_delete:
        shutil.rmtree('generate')
    colorama.init(convert=True)
    print(f'{Style.RESET_ALL}Done')


def num_frames(gentle: dict) -> int:
    frames = int(gentle['words'][-1]['end'] * 100)
    if args.crumple_zone:
        frames += 1000
    return frames


def find_poses() -> dict:
    # Parse script, output parsed script to generate
    raw_script = open(args.text, 'r').read()
    parsed_script = parse_script(raw_script)
    feeder_script = 'generate/script.txt'
    script_file = open(feeder_script, 'w+')
    script_file.write(parsed_script['feeder_script'])
    script_file.flush()
    script_file.close()

    poses_loc = []
    for word in range(len(parsed_script['marked_text'])):
        if parsed_script['marked_text'][word] == '¦':
            poses_loc.append(word)
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

    # Get gentle v_out
    stamps = gentle.align(args.audio, 'generate/script.txt')
    num_names = num_frames(stamps)
    ig.init(num_names)

    if args.no_delete:
        gentle_file = open('generate/gentle.json', 'w+')
        gentle_file.write(json.dumps(stamps, indent=4))
        gentle_file.flush()
        gentle_file.close()

    req_vid: ig.VideoRequest = args
    req_vid.poses_list = poses_list
    req_vid.poses_loc = script_blocks['poses_loc']

    ig.gen_vid(args)
    print_bar(num_names, num_names, "Generating Images: ")

    shutdown()
