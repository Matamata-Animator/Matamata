import os
import json
from PIL import Image
import cv2 as cv
import numpy as np
import random
from tqdm.auto import tqdm
import command
from colorama import Fore, Back, Style
import gentle

args = ''


def parse_script(text, start_character='[',
                 end_character=']'):  # Parse script to identify pose tags. start/end_character are by default set to brackets []
    start_character = start_character[0]
    end_character = end_character[0]
    poses = ['']
    recording = False
    num_poses = 0
    for i in text:
        if i == start_character and not recording:
            recording = True
            poses.append('')
            poses[num_poses] = start_character
        elif i == end_character:
            recording = False
            poses[num_poses] += end_character
            num_poses += 1
        else:
            if recording:
                poses[num_poses] += i

    # remove extra empty array entry
    del poses[-1]

    # remove tags from script
    for pose in poses:
        text = text.replace(pose, '¦')

    # create a list of words
    marked_text = text.replace('\n', ' ')
    marked_text = ' '.join(marked_text.split())
    marked_text = marked_text.split(' ')
    return {  # Out puts a dictionary with the list of poses, the script with markers of where
        'poses_list': poses,
        'marked_text': marked_text,
        'feeder_script': text.replace('¦', ' ')
    }


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
        'facePath': characters['facesFolder'] + pose['image'],
        'mouthPos': [pose['x'], pose['y']],
        'scale': characters['default_scale'] * pose['scale'],
        'mirror': [mirror_pose, mirror_mouth]
    }


def create_video(name, fPath, mPath, mScale, xPos, yPos, time, frame, totalTime, mirror, syl, video_list):
    skip = True
    if not args.skip_frames or syl == 1 or (time >= args.skip_thresh / args.framerate):
        skip = False

    if not skip:
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

        face.save(f'generate/{frame}.png')
        command.run(
            f'ffmpeg -loop 1 -i generate/{frame}.png -c:v libx264 -t {time} -pix_fmt yuv420p -r {args.framerate} -vf scale={args.scale} generate/{frame}.mp4')
        video_list.write(f'file {frame}.mp4\n')
    return [totalTime, frame + 1]


def gen_vid(inputs):
    global args
    args = inputs
    command.set_verbose(args.verbose)

    video_list = open('generate/videos.txt', 'w+')

    phone_reference = json.load(open(str(args.mouths), encoding='utf8'))
    characters_json = json.load(open(str(args.character), encoding='utf8'))

    # Counters:
    total_time = 0  # totalTime keeps a running total of how long the animation is at any given point.
    frame_counter = 0  # keeps track of which frame is currently being animated
    pose_counter = 0  # keeps track of which pose is currently being animated
    marked_counter = 0  # keeps track of which word in the script is being read

    # Remove and residual folders and processes from last time the program was run.

    # Parse script, output parsed script to generate
    raw_script = open(args.text, 'r').read()
    parsed_script = parse_script(raw_script)
    feeder_script = 'generate/script.txt'
    script_file = open(feeder_script, 'w+')
    script_file.write(parsed_script['feeder_script'])
    script_file.flush()
    script_file.close()
    poses_list = parsed_script['poses_list']
    marked_script = parsed_script['marked_text']
    if args.verbose:
        print(poses_list)

    # get output from gentle
    stamps = gentle.align(args.audio, feeder_script)

    # Make mouth closed until first phoneme
    pose = get_face_path(poses_list[pose_counter][1:-1], characters_json)

    face_path = pose['facePath']
    face = Image.open(face_path).convert('RGBA')

    mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']

    total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'], pose['mouthPos'][0],
                                             pose['mouthPos'][1],
                                             round(stamps['words'][0]['start'], 4) - float(args.offset), frame_counter,
                                             total_time, pose['mirror'], 1, video_list)

    marked_counter += 1  # Increase by 1 to get past the initial pose marker
    pose_counter += 1
    for w in tqdm(range(len(stamps['words']))):
        if marked_script[marked_counter] == '¦':
            pose = get_face_path(poses_list[pose_counter][1:-1], characters_json)

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
                                                         total_time, pose['mirror'], p, video_list)
        except:
            pass
        if w < len(stamps['words']) - 1:
            mouth_path = phone_reference['mouthsPath'] + 'closed.png'
            if stamps['words'][w + 1]['case'] == 'success':
                total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                         pose['mouthPos'][0], pose['mouthPos'][1],
                                                         round(stamps['words'][w + 1]['start'], 4) - total_time - float(
                                                             args.offset), frame_counter, total_time, pose['mirror'], 1,
                                                         video_list)
            else:
                total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'],
                                                         pose['mouthPos'][0], pose['mouthPos'][1], 0, frame_counter,
                                                         total_time, pose['mirror'], 1, video_list)

        marked_counter += 1
        print(' ', end='\r')
    mouth_path = phone_reference['mouthsPath'] + phone_reference['closed']
    total_time, frame_counter = create_video(frame_counter, face_path, mouth_path, pose['scale'], pose['mouthPos'][0],
                                             pose['mouthPos'][1], args.skip_thresh / args.framerate, frame_counter,
                                             total_time, pose['mirror'], 1, video_list)

    # Combine all videos into one video
    video_list.flush()
    video_list.close()

    # delete old output files
    if os.path.isfile(str(args.output)):
        os.remove(str(args.output))

    print('Finishing Up...')

    command.run(f'ffmpeg -i {args.audio} -f concat -safe 0 -i generate/videos.txt -c copy {args.output}')

    # delete all generate files
    # if os.path.isdir('generate'):
    #     shutil.rmtree('generate')
    command.run('docker kill gentle')
    command.run('docker rm gentle')
