import os
import json
from PIL import Image
import cv2 as cv
import random
from colorama import Fore, Back, Style
import sys

import command
import gentle
from bar import print_bar

args = ''
num_frames = 0


def init(phones):
    global num_phonemes
    num_phonemes = phones


def progress_bar(frames_completed):
    # print(f'\r{(f"[%-{num_phonemes-1}s] %d%%" % ("="*num_frames, 5*num_frames))}', end='')
    print_bar(frames_completed, num_phonemes, "Generating Images: ")


def get_face_path(pose, characters):
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
        'facePath': 'custom/' + characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': characters['default_scale'] * pose['scale'],
        'mirror': [mirror_pose, mirror_mouth]
    }


def create_video(name, fPath, mPath, mScale, xPos, yPos, time, frame, totalTime, mirror, syl, video_list, number):
    global num_frames
    if not args.skip_frames or syl == 1 or (time >= args.skip_thresh / args.framerate):
        time = round(time * args.framerate) / args.framerate
        time = max(1 / args.framerate, time)
        totalTime += time
        image = cv.imread(fPath, 0)
        face = Image.open(fPath).convert('RGBA')
        mouth = Image.open(mPath).convert('RGBA')
        mouth = mouth.resize([int(mouth.size[0] * mScale), int(mouth.size[1] * mScale)])

        width = image.shape[1]
        height = image.shape[0]
        mouth_pos = [xPos, yPos]
        if mirror[1]:
            mouth = mouth.transpose(Image.FLIP_LEFT_RIGHT)
        face.paste(mouth, (int(mouth_pos[0] - mouth.size[0] / 2), int(mouth_pos[1] - mouth.size[1] / 2)), mouth)

        if mirror[0]:
            face = face.transpose(Image.FLIP_LEFT_RIGHT)

        face.save(f'generate/{number}/{frame}.png')
        command.run(
            f'ffmpeg -loop 1 -i generate/{number}/{frame}.png -c:v libx264 -t {time} -pix_fmt yuv420p -r {args.framerate} -vf scale={args.scale} generate/{number}/{frame}.mp4')
        video_list.write(f'file {frame}.mp4\n')
        num_frames += 1
        progress_bar(num_frames)
    return [totalTime, frame + 1]


def gen_vid(inputs, poses_list, marked_script, number):
    global args
    args = inputs
    command.set_verbose(args.verbose)
    feeder_script = f'generate/feeder_scripts/{number}.txt'

    os.makedirs(f'generate/{number}')
    video_list = open(f'generate/{number}/videos.txt', 'w+')

    phone_reference = json.load(open(str(args.mouths), encoding='utf8'))
    characters_json = json.load(open(str(args.character), encoding='utf8'))

    # Counters:
    total_time = 0  # totalTime keeps a running total of how long the animation is at any given point.
    frame_counter = 0  # keeps track of which frame is currently being animated
    pose_counter = 0  # keeps track of which pose is currently being animated
    marked_counter = 0  # keeps track of which word in the script is being read

    if args.verbose:
        print(poses_list)

    # get output from gentle
    stamps = gentle.align(args.audio, feeder_script)

    # Make mouth closed until first phoneme
    # pose = get_face_path(poses_list[pose_counter][1:-1], characters_json)
    try:
        pose = get_face_path(poses_list[0][1:-1], characters_json)
    except:
        pass
    poses_list.pop(0)

    face_path = pose['facePath']
    face = Image.open(face_path).convert('RGBA')

    mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']

    try:
        total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                 pose['mouthPos'][0],
                                                 pose['mouthPos'][1],
                                                 round(stamps['words'][0]['start'], 4) - args.offset, frame_counter,
                                                 total_time, pose['mirror'], 1, video_list, number)
    except:
        total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                 pose['mouthPos'][0],
                                                 pose['mouthPos'][1],
                                                 args.offset / 2,
                                                 frame_counter,
                                                 total_time, pose['mirror'], 1, video_list, number)

    marked_counter += 1  # Increase by 1 to get past the initial pose marker
    pose_counter += 1
    for w in range(len(stamps['words'])):
        if marked_script[marked_counter] == '¦':
            try:
                pose = get_face_path(poses_list[0][1:-1], characters_json)
            except:
                pass

            face_path = pose['facePath']
            face = Image.open(face_path).convert('RGBA')

            marked_counter += 1
            pose_counter += 1

        word = stamps['words'][w]
        word_time = 0
        try:
            for p in range(len(word['phones'])):
                # Identify current phone
                phone = (word['phones'][p]['phone']).split('_')[0]
                word_time += word['phones'][p]['duration']
                # Reference phonemes.json to see which mouth goes with which phone
                mouth_path = 'mouths/' + (phone_reference['phonemes'][phone]['image'])

                total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                         pose['mouthPos'][0], pose['mouthPos'][1],
                                                         word['phones'][p]['duration'], frame_counter,
                                                         total_time, pose['mirror'], p, video_list, number)
        except:
            pass
        if w < len(stamps['words']) - 1:
            mouth_path = phone_reference['mouthsPath'] + 'closed.png'
            if stamps['words'][w + 1]['case'] == 'success':
                total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                         pose['mouthPos'][0], pose['mouthPos'][1],
                                                         round(stamps['words'][w + 1]['start'], 4) - total_time - float(
                                                             args.offset), frame_counter, total_time, pose['mirror'], 1,
                                                         video_list, number)
            else:
                total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                         pose['mouthPos'][0], pose['mouthPos'][1], 0, frame_counter,
                                                         total_time, pose['mirror'], 1, video_list, number)

        marked_counter += 1
    mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
    total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'], pose['mouthPos'][0],
                                             pose['mouthPos'][1], args.skip_thresh / args.framerate, frame_counter,
                                             total_time, pose['mirror'], 1, video_list, number)

    # Combine all videos into one video
    video_list.flush()
    video_list.close()

    # gets the name of the last video in videos.txt, and pauses until it is a file
    last_vid = open(f'generate/{number}/videos.txt').read().split('\n')[-2].split(' ')[1]
    while not os.path.isfile(f'generate/{number}/{last_vid}'):
        pass

    vid_name = f'{number}.{args.output.split(".")[-1]}'
    command.run(
        f'ffmpeg -i {args.audio} -f concat -safe 0 -i generate/{number}/videos.txt -c copy generate/videos/{vid_name}')
    videos_list = open('generate/videos/videos.txt', 'a')
    videos_list.write(f'file {vid_name}\n')
    videos_list.close()
