import os
import json

import cv2
import numpy as np

from colorama import Fore, Back, Style
import colorama

import command
import gentle
from bar import print_bar

import copy
import threading

import time
threads = []


class LockingCounter():
    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0

    def increment(self):
        with self.lock:
            self.count += 1


q = LockingCounter()

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
    if split_pose[0] in characters:
        pose = characters[split_pose[0]]  # splits to remove directional tag
    else:
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


def get_dimensions(path, scaler) -> str:
    face = cv2.imread(path)
    w, h = face.shape[1::-1]
    return f'{w * scaler}:{h * scaler}'


class FrameRequest:
    face_path: str = ''
    mouth_path: str = ''
    mouth_scale: float = 1
    mouth_x: int = 0
    mouth_y: int = 0
    duration: float = ''
    mirror_face: bool = False
    mirror_mouth: bool = False
    frame: int = 0
    folder_name: str = 'images'
    framerate = 100
    dimensions: str = "TBD"
    scaler: float = 1


def num_frames(frame_req: FrameRequest) -> int:
    return int(frame_req.duration * 100)


def gen_frames(frame_req: FrameRequest, d):
    global q
    frame_req.duration = round(frame_req.duration, 2)

    face = cv2.imread(frame_req.face_path, cv2.IMREAD_UNCHANGED)
    scale = (int(face.shape[1] * frame_req.scaler), int(face.shape[0] * frame_req.scaler))
    face = cv2.resize(face, scale)

    mouth = cv2.imread(frame_req.mouth_path, cv2.IMREAD_UNCHANGED)
    scale = (int(mouth.shape[1] * frame_req.mouth_scale * frame_req.scaler),
             int(mouth.shape[0] * frame_req.mouth_scale * frame_req.scaler))
    mouth = cv2.resize(mouth, scale)
    if frame_req.mirror_face:
        mouth = cv2.flip(mouth, 1)
    if frame_req.mirror_mouth:
        face = cv2.flip(face, 1)

    centered_x = int((frame_req.mouth_x) * frame_req.scaler)
    centered_y = int((frame_req.mouth_y) * frame_req.scaler)
    height, width, depth = mouth.shape

    for my, y in enumerate(range(centered_y - int(height / 2), centered_y + int(height / 2))):
        for mx, x in enumerate(range(centered_x - int(width / 2), centered_x + int(width / 2))):
            if mouth[my, mx][-1] != 0 or len(mouth[my, mx]) <= 3:
                for i, c in enumerate(face[y, x]):
                    if i < len(mouth[my, mx]):
                        face[y, x][i] = mouth[my, mx][i]
    # face[centered_y: centered_y + height, centered_x: centered_x + width ] = mouth
    image_path = f'generate/{frame_req.folder_name}/{frame_req.frame}.png'
    cv2.imwrite(image_path, face)

    q.increment()

    for frame in range(int(frame_req.duration * 100)):
        image_path = f'generate/{frame_req.folder_name}/{frame_req.frame + frame}.png'
        cv2.imwrite(image_path, face)
        q.increment()

    # wait for image
    while not os.path.isfile(image_path):
        pass


def update_pose_from_timestamps(frame, timestamps, poses_loc, fc, pose):
    for p in range(len(timestamps)):
        if frame.frame >= timestamps[p]['time'] and timestamps[p]['time'] != 0:

            pose = get_face_path(timestamps[p]['pose'])
            frame.face_path = pose['face_path']
            frame.mouth_scale = pose['scale']
            frame.mirror_face = pose['mirror_face']
            frame.mirror_mouth = pose['mirror_mouth']
            frame.mouth_x = pose['mouth_pos'][0]
            frame.mouth_y = pose['mouth_pos'][1]
            frame.frame = fc
            # decrement each loc because each previous loc is an additional 'word' in the script in animate.py
            for loc in range(len(poses_loc)):
                poses_loc[loc] -= 1
    return frame, poses_loc, pose


class VideoRequest:
    audio: str = ''
    text: str = ''
    mouths: str = ''
    characters: str = ''

    skip_frames: bool = False
    skip_thresh: float = ''

    framerate: int = 100
    dimensions: str = ''
    dimension_scaler: float = 1

    verbose: bool = ''

    offset: float = ''

    poses_list: list = ''
    poses_loc: list = ''

    crumple_zone: bool = False

    timestamps: list = []


def gen_vid(req: VideoRequest):
    # set up process vars
    global verbose
    global characters
    global threads

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
    # if using timestamps, see if pose should be swapped
    frame, req.poses_loc, pose = update_pose_from_timestamps(frame, req.timestamps, req.poses_loc,
                                                             frame_counter, pose)

    frame.face_path = pose['face_path']
    frame.mouth_scale = pose['scale']
    frame.mirror_face = pose['mirror_face']
    frame.mirror_mouth = pose['mirror_mouth']
    frame.mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
    frame.mouth_x = pose['mouth_pos'][0]
    frame.mouth_y = pose['mouth_pos'][1]
    frame.frame = frame_counter
    frame.scaler = req.dimension_scaler
    if req.dimensions == 'TBD':
        req.dimensions = get_dimensions(pose['face_path'], req.dimension_scaler)
    total_time = req.offset / 100
    for w in range(len(gentle_out['words'])):
        word = gentle_out['words'][w]
        if word['case'] == 'success' and 'phones' in word:
            # keep mouth closed between last word and this word
            # duration = word['start'] - last_animated_word_end
            duration = word['start'] - total_time

            if duration > 0:
                frame.mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
                frame.frame = frame_counter

                frame.duration = duration
                frame.duration = frame.duration
                total_time += frame.duration

                # gen_frames(copy.deepcopy(frame))
                threads.append(threading.Thread(target=gen_frames, args=(copy.deepcopy(frame), q, )))
                threads[-1].start()

                frame_counter += num_frames(frame)

            # if using timestamps, see if pose should be swapped
            frame, req.poses_loc, pose = update_pose_from_timestamps(frame, req.timestamps,
                                                                     req.poses_loc,
                                                                     frame_counter, pose)

            # change pose
            if len(req.poses_loc) > 0 and int(req.poses_loc[0]) == int(w) and len(req.timestamps) == 0:
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
            for p in range(len(word['phones'])):
                phone = (word['phones'][p]['phone']).split('_')[0]
                frame.mouth_path = phone_reference['mouthsPath'] + phone_reference['phonemes'][phone]['image']
                frame.duration = word['phones'][p]['duration']
                frame.frame = frame_counter
                total_time += frame.duration
                # frame_counter = gen_frames(frame, q)
                threads.append(threading.Thread(target=gen_frames, args=(copy.deepcopy(frame), q,)))
                threads[-1].start()
                frame_counter += num_frames(frame)

            last_animated_word_end = word['end']

    # make mouth closed at the end
    frame.mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
    frame.frame = frame_counter

    if req.crumple_zone:
        frame.duration = frame.framerate / 10
    else:
        frame.duration = 0.01
    threads.append(threading.Thread(target=gen_frames, args=(copy.deepcopy(frame), q,)))
    threads[-1].start()

    frame_counter += num_frames(frame)

    while q.count <= num_phonemes:
        progress_bar(q.count)

    for t in threads:
        t.join()
    return req.dimensions
