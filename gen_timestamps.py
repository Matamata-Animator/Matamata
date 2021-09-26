def gen_timestamps(path):
    """
    Generate the timestamps array from a file

    :param str path: Path to the timestamps file
    :return:Array of dictionaries containing the name of a pose and the time in milliseconds
    """
    ts = open(path, 'r').read()
    ts = ts.split('\n')
    stamps = []
    for line in ts:
        if line != '':
            line = line.split(' ')
            stamp = {
                'time': int(line[0]) / 10,
                'pose': f'[{line[1]}]'
            }
            stamps.append(stamp)
    return stamps
