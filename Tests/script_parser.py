
script = open('test-1.txt', 'r', encoding='utf-8').read()

def parseScript(text, startCharacter, endCharacter):
    startCharacter = startCharacter[0]
    endCharacter = endCharacter[0]
    poses = [""]
    recording = False;
    numPoses = 0;

    for i in text:
        if i == startCharacter and not recording:
            recording = True
            poses.append("")
        elif i == endCharacter:
            recording = False
            numPoses += 1
        else:
            if recording:
                poses[numPoses] += i
    del poses[-1] #remove extra empty array entry

    #remove tags from script
    for pose in poses:
        text = text.replace(startCharacter + pose + endCharacter, "¦")
    return [poses, text]
reee =  (parseScript(script, '[', ']'))

out = open('out.txt', 'w+', encoding='utf-8')
out.write(reee[1])
out.flush()
out.close()

print(reee[0])
