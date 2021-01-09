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
        raise Exception(Fore.RED + '[ERR 412] Failed to load pose: ' + pose)

    # determine whether to flip image
    mirror_pose = False
    mirror_mouth = False
    looking_left = True
    if len(split_pose) == 2:
        if split_pose[1].lower() == 'right' or split_pose[1].lower() == 'r':
            looking_left = False
        if 'facingLeft' in pose and looking_left != pose['facingLeft']:
            mirror_pose = True
    if not pose['facingLeft']:
        mirror_mouth = True

    scale = 1
    if 'default_scale' in characters:
        scale = characters['default_scale']
    if 'scale' in pose:
        scale *= pose['scale']
    return {
        'facePath': characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': scale,
        'mirror': [mirror_pose, mirror_mouth]
    }


class FrameRequest:
    face_path: str = get_face_path('default')['facePath']
    mouth_path: str = ''
    mouth_scale: float = 1
    mouth_x: int = ''
    mouth_y: int = ''
    duration: float = ''
    mirror_face: bool = False
    mirror_mouth: bool = False
    video_list = ''
    frame: int = 0
    number: int = 0


def gen_frames(frame_req: FrameRequest):
    face = Image.open(frame_req.face_path).convert('RGBA')
    mouth = Image.open(frame_req.mouth_path).convert('RGBA')
    mouth = mouth.resize([int(mouth.size[0] * frame_req.mouth_scale), int(mouth.size[1] * frame_req.mouth_scale)])

    mouth_pos = [frame_req.x_pos, frame_req.y_pos]
    if frame_req.mirror_face:
        mouth = mouth.transpose(Image.FLIP_LEFT_RIGHT)
    if frame_req.mirror_mouth:
        face = face.transpose(Image.FLIP_LEFT_RIGHT)
    face.save(f'generate/{frame_req.number}/{frame_req.frame}.png')

    command.run(
        f'ffmpeg -loop 1 -i generate/{frame_req.number}/{frame_req.frame}.png -c:v libx264 -t {frame_req.duration} -pix_fmt yuv420p -r {frame_req.framerate} -vf scale={frame_req.scale} generate/{frame_req.number}/{frame_req.frame}.mp4')
    FrameRequest.write(f'file {frame_req.frame}.mp4\n')
    face.paste(mouth, (int(mouth_pos[0] - mouth.size[0] / 2), int(mouth_pos[1] - mouth.size[1] / 2)), mouth)
    progress_bar(frame_req.frame)


class VideoRequest:
    audio: str = ''
    text: str = ''
    mouths: str = ''
    characters: str = ''

    skip_frames: bool = False
    skip_thresh: float = ''

    framerate: int = 100
    scale: float = ''

    verbose: bool = ''

    offset: float = ''

    poses_list: list = ''
    poses_loc: list = ''


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

