import json
import math
import time

import cv2
import numpy as np

from colorama import Fore, Back, Style
import colorama

import gentle
from bar import print_bar

import copy
import threading

import colorsys

threads = []

frames = []


class LockingCounter():
    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0

    def increment(self, num=1):
        with self.lock:
            self.count += num
            progress_bar(self.count)


q = LockingCounter()

verbose = False
characters = ''

num_phonemes = 1


def init(phones):
    """
    Init image generator

    :param phones: Gentle output
    :return:
    """
    global num_phonemes
    global frames
    num_phonemes = phones
    colorama.init(convert=True)

    frames = [0] * num_phonemes


def v_out(log):
    if verbose:
        print(log)


def progress_bar(frames_completed):
    print_bar(frames_completed, num_phonemes, "Generating Images: ")


def get_face_path(pose, phone_reference):
    """
    Get pose information from pose name.

    :param str pose: Pose name
    :param dict phone_reference: Phonemes.json
    :return:
    face_path,
        mouth_pos,
        scale,
        mirror_face,
        mirror_mouth,
        closed_mouth

    """
    split_pose = pose[1:-1].split('-')
    if split_pose[0] in characters:
        pose = characters[split_pose[0]]  # splits to remove directional tag
    else:
        raise Exception(Fore.RED + '[ERR 412] Failed to load pose: ' + pose)

    # determine whether to flip image
    mirror_pose = False
    mirror_mouth = False

    looking_right = True
    if len(split_pose) == 2:
        if split_pose[1].lower() == 'left' or split_pose[1].lower() == 'l':
            looking_right = True

        if 'facingRight' in pose and looking_right != pose['facingRight']:
            mirror_pose = True
    if 'facingRight' in pose and not pose['facingRight']:
        mirror_mouth = True

    scale = 1
    if 'default_scale' in characters:
        scale = characters['default_scale']
    if 'scale' in pose:
        scale *= pose['scale']

    if 'closed_mouth' in pose:
        closed_mouth = pose['closed_mouth']
    else:
        closed_mouth = phone_reference['closed']

    return {
        'face_path': characters['facesFolder'] + pose['image'],
        'mouth_pos': [pose['x'], pose['y']],
        'scale': float(scale),
        'mirror_face': mirror_pose,
        'mirror_mouth': mirror_mouth,
        'closed_mouth': closed_mouth
    }


def get_dimensions(path, scaler) -> str:
    """
    Get scaled dimensions of an image.

    :param str path: Path to image
    :param float scaler: Amount to scale by (default=1)
    :return str: width:height
    """
    face = cv2.imread(path)
    w, h = face.shape[1::-1]
    return f'{math.ceil(w * scaler / 2) * 2}:{math.ceil(h * scaler / 2) * 2}'


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
    """
    Get the number of frames that should be in the video

    :param frame_req: Frame Request
    :return int: num_frames
    """
    return int(frame_req.duration * 100)


def overlay(base, top, x, y, scale):
    """
    Place an image onto another

    :param numpy.ndarray base: Base image
    :param numpy.ndarray top: Overlayed image
    :param int x: x coord of top
    ":param int y: y coord of top
    :param float scale:
    :return:
    """
    centered_x = int(x * scale)
    centered_y = int(y * scale)
    height, width = top.shape[:2]

    for my, y in enumerate(range(centered_y - int(height / 2), centered_y + int(height / 2))):
        for mx, x in enumerate(range(centered_x - int(width / 2), centered_x + int(width / 2))):
            fp = base[y, x]
            mp = top[my, mx]
            if mp[-1] == 255 or len(mp) <= 3:
                fp[:3] = mp[:3]
            elif mp[-1] != 0:
                fp[:3] = ablend(mp[-1], mp, fp)
    return base


def gen_frame(frame_req: FrameRequest) -> list:
    """
    Create a single frame from a frame request

    :param FrameRequest frame_req: Frame request
    :return: frame
    """
    face = cv2.imread(frame_req.face_path)

    size = frame_req.dimensions.split(':')
    size = [int(i) for i in size]
    scale = (int(size[0] * frame_req.scaler), int(size[1] * frame_req.scaler))
    face = cv2.resize(face, scale)

    mouth = cv2.imread(frame_req.mouth_path, cv2.IMREAD_UNCHANGED)
    scale = (int(mouth.shape[1] * frame_req.mouth_scale * frame_req.scaler),
             int(mouth.shape[0] * frame_req.mouth_scale * frame_req.scaler))
    mouth = cv2.resize(mouth, scale)
    if frame_req.mirror_face:
        mouth = cv2.flip(mouth, 1)
    if frame_req.mirror_mouth:
        face = cv2.flip(face, 1)

    face = overlay(face, mouth, frame_req.mouth_x, frame_req.mouth_y, frame_req.scaler)

    return face


def write_frames(frame_req: FrameRequest, d=None):
    """
    Create frames from a frame request and write them to the array of frames

    :param frame_req: Frame Request
    :param None d: None
    :return: Frame counter after the current frames are written
    """
    global q
    global frames

    frame_req.duration = round(frame_req.duration, 2)

    face = gen_frame(frame_req)

    start = int(frame_req.frame)
    end = int(frame_req.frame + frame_req.duration * 100)
    frames[start:end] = [face] * int(frame_req.duration * 100)
    q.increment(int(frame_req.duration * 100) + 1)

    return frame_req.frame + frame_req.duration * 100


def ablend(a, fg, bg) -> list:
    """
    Blend the colors of two pixels

    :param int a: Opacity
    :param numpy.ndarray fg: Foreground pixel
    :param numpy.ndarray bg: Base pixel
    :return numpy.ndarray: Blended pixel
    """
    a /= 255

    fhsv = np.array(colorsys.rgb_to_hsv(*fg[:3]))
    bhsv = np.array(colorsys.rgb_to_hsv(*bg[:3]))
    blend = (fhsv * a + bhsv * (1 - a))

    blend = colorsys.hsv_to_rgb(*blend)
    blend = [int(i) for i in blend]

    return blend


def update_pose_from_timestamps(frame: FrameRequest, timestamps, poses_loc, fc, pose, phone_references):
    """
    Get the current pose from the timestamps array

    :param FrameRequest frame: Current frame requesrt
    :param list timestamps: Timestamps array
    :param list poses_loc:
    :param int fc: Frame Counter
    :param pose: Current pose
    :param phone_references: phonemes.json
    :return: new frame request, poses_loc, new pose
    """
    for p in range(len(timestamps)):
        if frame.frame >= timestamps[p]['time']:

            pose = get_face_path(timestamps[p]['pose'], phone_references)
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

    cache: bool = False

    port: int = 8765

    stamps = {}


def gen_vid(req: VideoRequest):
    """
    Generate video from frame request

    :param VideoRequest req: Video Request
    :return: Array of frames
    """

    # set up process vars
    global verbose
    global characters
    global threads

    global frames

    characters = json.load(open(req.character, 'r'))

    verbose = req.verbose
    phone_reference = json.load(open(str(req.mouths), encoding='utf8'))

    # get gentle of text
    gentle_out = req.stamps
    # gentle_out = gentle.align(req.audio, req.text, req.port)
    v_out(gentle_out)

    frame = FrameRequest()
    frame_counter = 0

    # set pose to be default, set mouth to be closed
    pose = get_face_path(req.poses_list[0], phone_reference)
    # if using timestamps, see if pose should be swapped
    frame, req.poses_loc, pose = update_pose_from_timestamps(frame, req.timestamps, req.poses_loc,
                                                             frame_counter, pose, phone_reference)

    frame.face_path = pose['face_path']
    frame.mouth_scale = pose['scale']
    frame.mirror_face = pose['mirror_face']
    frame.mirror_mouth = pose['mirror_mouth']
    frame.mouth_path = phone_reference['mouthsPath'] + pose['closed_mouth']
    frame.mouth_x = pose['mouth_pos'][0]
    frame.mouth_y = pose['mouth_pos'][1]
    frame.frame = frame_counter
    frame.scaler = req.dimension_scaler
    if req.dimensions == 'TBD':
        req.dimensions = get_dimensions(pose['face_path'], req.dimension_scaler)
        frame.dimensions = req.dimensions
    total_time = req.offset / 100
    for w in range(len(gentle_out['words'])):
        word = gentle_out['words'][w]
        if word['case'] == 'success' and 'phones' in word:
            # keep mouth closed between last word and this word
            duration = word['start'] - total_time

            if duration > 0:
                frame.mouth_path = phone_reference['mouthsPath'] + pose['closed_mouth']
                frame.frame = frame_counter

                frame.duration = duration
                frame.duration = frame.duration
                total_time += frame.duration

                frame_counter = write_frames(frame, q)

            # if using timestamps, see if pose should be swapped
            frame, req.poses_loc, pose = update_pose_from_timestamps(frame, req.timestamps,
                                                                     req.poses_loc,
                                                                     frame_counter, pose, phone_reference)

            # change pose
            if len(req.poses_loc) > 0 and int(req.poses_loc[0]) == int(w) and len(req.timestamps) == 0:
                pose = get_face_path(req.poses_list.pop(0), phone_reference)
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
                threads.append(threading.Thread(target=write_frames, args=(copy.deepcopy(frame), q,)))
                threads[-1].start()
                frame_counter += num_frames(frame)

            last_animated_word_end = word['end']

    # make mouth closed at the end
    frame.mouth_path = phone_reference['mouthsPath'] + pose['closed_mouth']
    frame.frame = frame_counter

    if req.crumple_zone:
        frame.duration = frame.framerate / 10
    else:
        frame.duration = 0.05
    threads.append(threading.Thread(target=write_frames, args=(copy.deepcopy(frame), q,)))
    threads[-1].start()

    frame_counter += num_frames(frame)

    for t in threads:
        t.join()

    return frames
