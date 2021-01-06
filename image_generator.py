import os
import json
from PIL import Image
import random
from colorama import Fore, Back, Style
import colorama
import sys

import command
import gentle
from bar import print_bar

verbose = False
characters = ''


def init(phones):
    global num_phonemes
    num_phonemes = phones
    colorama.init(convert=True)


def out(log):
    if verbose:
        print(log)


def progress_bar(frames_completed):
    print_bar(frames_completed, num_phonemes, "Generating Images: ")


def get_face_path(pose):
    split_pose = pose.split('-')
    try:
        poses_list = characters[split_pose[0]]  # splits to remove directional tag
        pose = poses_list[min(random.randint(0, len(poses_list)), len(poses_list) - 1)]
    except:
        print(Fore.RED + '[ERR 412] Failed to load pose: ' + pose)
        print(Style.RESET_ALL)
        quit()

    # determine whether to flip image
    mirror_pose = False
    mirror_mouth = False
    looking_left = True
    if len(split_pose) == 2:
        if split_pose[1].lower() == 'right' or split_pose[1].lower() == 'r':
            looking_left = False
        if looking_left != pose['facingLeft']:
            mirror_pose = True
    if not pose['facingLeft']:
        mirror_mouth = True
    return {
        'facePath': characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': characters['default_scale'] * pose['scale'],
        'mirror': [mirror_pose, mirror_mouth]
    }


class FrameRequest:
    face_path = get_face_path('default')['facePath']
    mouth_path = ''
    mouth_scale = 1
    mouth_x = ''
    mouth_y = ''
    duration = ''
    mirror = False
    video_list = ''

def gen_frames(frame_req: FrameRequest):
    face = Image.open(frame_req.face_path).convert('RGBA')
    mouth = Image.open(frame_req.mouth_path).convert('RGBA')
    mouth = mouth.resize([int(mouth.size[0] * frame_req.mouth_scale), int(mouth.size[1] * frame_req.mouth_scale)])


    mouth_pos = [frame_req.x_pos, frame_req.y_pos]
    if frame_req.mirror[1]:
        mouth = mouth.transpose(Image.FLIP_LEFT_RIGHT)
    face.paste(mouth, (int(mouth_pos[0] - mouth.size[0] / 2), int(mouth_pos[1] - mouth.size[1] / 2)), mouth)

class VideoRequest:
    audio = ''
    text = ''
    mouths = ''
    characters = ''

    skip_frames = ''
    skip_thresh = ''

    framerate = ''
    scale = ''

    verbose = ''

    offset = ''

    poses_list = ''
    poses_loc = ''


def gen_vid(req: VideoRequest):
    global verbose
    global characters
    command.set_verbose(req.verbose)
    verbose = req.verbose
    characters = req.characters

    phone_reference = json.load(open(str(req.mouths), encoding='utf8'))
    characters_json = json.load(open(str(req.character), encoding='utf8'))

    gentle_out = gentle.align(req.audio, req.text)
    out(gentle_out)

    # set pose to be default, set mouth to be closed
    pose = get_face_path('default')
    face_path = pose['facePath']
    face = Image.open(face_path).convert('RGBA')

    mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']


