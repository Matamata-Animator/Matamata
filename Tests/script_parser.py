

script = open('test-1.txt', 'r').read()

def parseScript(text, startCharacter, endCharacter):
    startCharacter = startCharacter[0]
    endCharacter = endCharacter[0]
    poses = [""]
    recording = False;
    numPoses = 0;

    for i in text:
        if i == startCharacter:
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
    print(text)
    return [poses, text]
reee =  (parseScript(script, '[', ']')[1])
out = open('generate/script.txt', 'w+')
out.write(str(reee))
out.flush()
out.close()
