def parse_script(text, start_character='[', end_character=']'):  # Parse script to identify pose tags
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
