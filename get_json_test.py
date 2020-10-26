import time
from subprocess import Popen
import os

docker = Popen(['docker', 'run', '-p', '8765:8765', 'lowerquality/gentle'])
time.sleep(1)
r = os.system('curl -F "audio=@voice-test.mp3" -F "transcript=@words.txt" "http://localhost:8765/transcriptions?async=false"')
print(r)
