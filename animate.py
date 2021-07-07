import configargparse
from colorama import Fore, Style
import colorama
import os
import shutil
import json
from dotenv import load_dotenv

import emotion
import gentle
import transcriber
import image_generator as ig
from parse_script import parse_script

from gen_timestamps import gen_timestamps

import time

import cv2
import ffmpeg

import string
import random

# Arg Parse Stuff
parser = configargparse.ArgParser()

# Arguments
parser.add('--config', required=False, is_config_file=True, default='config.txt', help='config file path')

parser.add('-a', '--audio', required=True, type=str)

parser.add('-t', '--text', required=False, type=str, default='')
parser.add('-ts', '--timestamps', required=False, type=str, default='')

parser.add('-o', '--output', required=False, default='output.mp4', type=str)
parser.add('-cd', '--codec', required=False, default='avc1', type=str)

parser.add('-s', '--offset', required=False, default='0.00', type=float)

parser.add('-c', '--character', required=False, default='characters.json', type=str)
parser.add('-m', '---mouths', required=False, default='phonemes.json', type=str)

parser.add('-d', '--dimensions', required=False, default='TBD', type=str)
parser.add('-ds', '--dimension_scaler', required=False, default='1', type=float)

parser.add('-r', '--framerate', required=False, default=100, type=int)

parser.add('-em', '--emotion_detection_env', required=False, type=str)

# Flags
parser.add('--no_delete', required=False, default=False, action='store_true')

parser.add('-v', '--verbose', required=False, default=False, action='store_true')
parser.add('--crumple_zone', required=False, default=False, action='store_true')
parser.add('-nd', '--no_docker', required=False, default=False, action='store_true')

args = parser.parse_args()
port = 8765
args.container_name = 'gentle'

if args.emotion_detection_env and args.timestamps:
    parser.error("Emotion detection and timestamp mode are currently mutually exclusive. Sorry!")

banner = '''
  __  __       _                        _        
 |  m/  | __ _| |_ __ _ _ __ ___   __ _| |_ __ _ 
 | |m/| |/ _` | __/ _` | '_ ` _ m / _` | __/ _` |
 | |  | | (_| | || (_| | | | | | | (_| | || (_| |
 |_|  |_|m__,_|m__m__,_|_| |_| |_|m__,_|m__m__,_|
                                                 
'''


def init():
    # Print banner
    colorama.init(convert=True)
    print(Fore.GREEN)
    print(banner.replace('m', '\\'))
    print(Style.RESET_ALL)

    client = None
    if not args.no_docker:
        gentle.remove_old(args.container_name)
        print("Booting Gentle...")
        client = gentle.init('lowerquality/gentle', args.container_name, port)

    # Delete old folder, then create the new ones
    shutil.rmtree('generate', ignore_errors=True)
    while os.path.isdir('generate'):
        shutil.rmtree('generate', ignore_errors=True)
        time.sleep(0.01)

    os.makedirs('generate/')

    return client


def shutdown(frames, container) -> None:
    if not args.no_docker:
        gentle.terminate(container)

    print('\nCombining Frames...')
    size = frames[0].shape[1], frames[0].shape[0]
    fourcc = cv2.VideoWriter_fourcc(*args.codec)
    video = cv2.VideoWriter("generate/cv.mp4", fourcc, 100.0, size)
    i = 0

    for c, f in enumerate(frames):
        i += 1
        try:
            video.write(f)
            i = 0
        except:
            print(f'Error writing frame {c}. Attempting automatic fix...')
            i += 1
            video.write(frames[c - i])

    video.release()

    # delete old output files
    if os.path.isfile(args.output):
        os.remove(args.output)
    print('\nFinishing Up...')

    export_video = ffmpeg.input('generate/cv.mp4', )
    export_audio = ffmpeg.input(args.audio)
    ffmpeg.concat(export_video, export_audio, v=1, a=1).output(args.output, loglevel='quiet').run()

    while not os.path.isfile(args.output):
        pass
    if not args.no_delete:
        shutil.rmtree('generate')
    colorama.init(convert=True)
    print(f'{Style.RESET_ALL}Done')


def num_frames(gentle: dict) -> int:
    frames = int(gentle['words'][-1]['end'] * 100 - args.offset)
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
    container = init()

    if args.text == '':
        print('Transcribing Audio...')
        args.text = 'generated_script.txt'
        transcriber.create_script(args.audio)

    if args.emotion_detection_env:
        print('Detecting Emotions...')
        load_dotenv(dotenv_path=args.emotion_detection_env)

        emotion.init(api_url=os.getenv("TONE_ANALYZER_URL"), api_key=os.getenv("TONE_ANALYZER_IAM_APIKEY"))
        emotion.save_emotions(args.text, 'script_with_emotions.txt')

        response = input('Emotions generated. Please confirm that the generated poses are correct (Y/N)')
        if response.lower() != 'y':
            exit()
        args.text = 'script_with_emotions.txt'

    timestamps = []
    if args.timestamps != '':
        print('Generating Timestamps...')
        timestamps = gen_timestamps(args.timestamps)

    while not gentle.is_ready(port):
        print("Waiting for gentle...")


    # Generate the feeder script, get poses list, and where each pose should go in the script.
    print('Analyzing Text...')
    script_blocks = find_poses()
    poses_list = script_blocks['poses_list']

    # Get gentle v_out
    stamps = gentle.align(args.audio, 'generate/script.txt', port)
    num_names = num_frames(stamps)
    ig.init(num_names)

    if args.no_delete:
        gentle_file = open('generate/gentle.json', 'w+')
        gentle_file.write(json.dumps(stamps, indent=4))
        gentle_file.flush()
        gentle_file.close()

    req_vid: ig.VideoRequest = args
    req_vid.stamps = stamps
    req_vid.port = port
    req_vid.timestamps = timestamps
    req_vid.poses_list = poses_list
    req_vid.poses_loc = script_blocks['poses_loc']

    frames = ig.gen_vid(args)

    shutdown(frames, container)
