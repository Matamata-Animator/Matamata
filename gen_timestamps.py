def gen_timestamps(path):
    ts = open(path, 'r').read()
    ts = ts.split('\n')
    stamps = []
    for line in ts:
        if line != '':
            line = line.split(' ')
            stamp = {
                'time': int(line[0])/10,
                'pose': f'[{line[1]}]'
            }
            stamps.append(stamp)
    return stamps