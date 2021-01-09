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

num_phonemes = 1
def init(phones):
    global num_phonemes
    num_phonemes = phones
    colorama.init(convert=True)


def v_out(log):
    if verbose:
        print(log)


def progress_bar(frames_completed):
    print_bar(frames_completed, num_phonemes, "Generating Images: ")


def get_face_path(pose):
    split_pose = pose[1:-1].split('-')
    try:
        poses_list = characters[split_pose[0]]  # splits to remove directional tag
        pose = poses_list[0]
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
    if 'facingLeft' in pose and not pose['facingLeft']:
        mirror_mouth = True

    scale = 1
    if 'default_scale' in characters:
        scale = characters['default_scale']
    if 'scale' in pose:
        scale *= pose['scale']

    return {
        'face_path': characters['facesFolder'] + pose['image'],
        'mouth_pos': [pose['x'], pose['y']],
        'scale': float(scale),
        'mirror_face': mirror_pose,
        'mirror_mouth': mirror_mouth
    }


class FrameRequest:
    face_path: str = ''
    mouth_path: str = ''
    mouth_scale: float = 1
    mouth_x: int = 0
    mouth_y: int = 0
    duration: float = ''
    mirror_face: bool = False
    mirror_mouth: bool = False
    video_list = ''
    frame: int = 0
    folder_name: str = 'images'
    framerate = 100
    scale: float = 1


def gen_frames(frame_req: FrameRequest) -> int:
    face = Image.open(frame_req.face_path).convert('RGBA')
    mouth = Image.open(frame_req.mouth_path).convert('RGBA')
    mouth = mouth.resize([int(mouth.size[0] * frame_req.mouth_scale), int(mouth.size[1] * frame_req.mouth_scale)])

    if frame_req.mirror_face:
        mouth = mouth.transpose(Image.FLIP_LEFT_RIGHT)
    if frame_req.mirror_mouth:
        face = face.transpose(Image.FLIP_LEFT_RIGHT)
    centered_x = int(frame_req.mouth_x - mouth.size[0] / 2)
    centered_y = int(frame_req.mouth_y - mouth.size[1] / 2)
    mouth_pos = (centered_x, centered_y)
    face.paste(mouth, mouth_pos, mouth)

    face.save(f'generate/{frame_req.folder_name}/{frame_req.frame}.png')

    command.run(
        f'ffmpeg -loop 1 -i generate/{frame_req.folder_name}/{frame_req.frame}.png -c:v libx264 -t {frame_req.duration} -pix_fmt yuv420p -r {frame_req.framerate} generate/{frame_req.folder_name}/{frame_req.frame}.mp4')
    # FrameRequest.write(f'file {frame_req.frame}.mp4\n')
    progress_bar(frame_req.frame)

    return  frame_req.frame+1

class VideoRequest:
    audio: str = ''
    text: str = ''
    mouths: str = ''
    characters: str = ''

    skip_frames: bool = False
    skip_thresh: float = ''

    framerate: int = 100
    scale: float = 1

    verbose: bool = ''

    offset: float = ''

    poses_list: list = ''
    poses_loc: list = ''


def gen_vid(req: VideoRequest):
    # set up process vars
    global verbose
    global characters
    characters = json.load(open(req.character, 'r'))
    command.set_verbose(req.verbose)
    verbose = req.verbose
    phone_reference = json.load(open(str(req.mouths), encoding='utf8'))

    # get gentle of text
    gentle_out = gentle.align(req.audio, req.text)
    v_out(gentle_out)

    frame = FrameRequest()
    frame_counter = 0

    # set pose to be default, set mouth to be closed
    pose = get_face_path(req.poses_list[0])
    frame.face_path = pose['face_path']
    frame.mouth_scale = pose['scale']
    frame.mirror_face = pose['mirror_face']
    frame.mirror_mouth = pose['mirror_mouth']
    frame.mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
    frame.mouth_x = pose['mouth_pos'][0]
    frame.mouth_y = pose['mouth_pos'][1]
    frame.frame = frame_counter


    #Keep mouth closed until first word
    word_counter = 0
    while gentle_out['words'][word_counter]['case'] != 'success':
        word_counter += 1
    frame.duration = gentle_out['words'][word_counter]['start']
    frame_counter = gen_frames(frame)

    for word in range(len(gentle_out['words'])):
        if len(req.poses_loc) > 0 and int(req.poses_loc[0]) == int(word):
            pose = get_face_path(req.poses_list.pop(0))
            req.poses_loc.pop(0)

            frame.face_path = pose['face_path']
            frame.mouth_scale = pose['scale']
            frame.mirror_face = pose['mirror_face']
            frame.mirror_mouth = pose['mirror_mouth']
            frame.mouth_x = pose['mouth_pos'][0]
            frame.mouth_y = pose['mouth_pos'][1]
            frame.frame = frame_counter
            # decrement each loc because each previous loc is an additional 'word' in the script in animate.py
            for loc in range(len(req.poses_loc)):
                req.poses_loc[loc] -= 1

        # each phoneme in a word
        if gentle_out['words'][word]['case'] == 'success' and 'phones' in gentle_out['words'][word]:
            for p in range(len(gentle_out['words'][word]['phones'])):
                pass




if __name__ == '__main__':
    from colorama import Fore, Back, Style
    import shutil
    colorama.init(convert=True)
    print(Fore.GREEN)
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

    pose = get_face_path('default')

    frame = FrameRequest()
    frame.mouth_scale = pose['scale']
    frame.mouth_path = 'mouths/closed.png'
    frame.mouth_x = 103
    frame.mouth_y = 199
    frame.folder_name = 'videos'
    frame.duration = 1
    gen_frames(frame)