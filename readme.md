# Auto Lip Sync

This is the auto-lip-sync tool created by AI Spawn.

## Installation

### Windows

This tool was made to be more convenient for people, and since the majority of people, including me, only use Windows on a daily basis, it was essential for this to be able to run on Windows. That being said, there are a few external programs required to make this run.

Install:

* [Docker Desktop](https://www.docker.com/get-started)
* [Anaconda](https://www.anaconda.com/products/individual), or a similar python environment that allows you to use pip. This is  just the one I recommend.

Open 'Anacaona Prompt'

Clone the repo

> git clone https://github.com/AI-Spawn/Auto-Lip-Sync

Install required packages

> pip install -r requirements.txt
>
> conda install ffmpeg

Launch Docker if it isn't launched already

> docker pull lowerquality/gentle



## Setup

### Recording

This tool works best when you talk at a constant pace. It also works best when your audio is clear, so speak clearly, consistently, and I recommend using a program like [audacity](https://www.audacityteam.org/download/) (free).

### Script

The script should be a text document with a transcript of audio, and poses in-between brackets. For instance, if the audio read:

> The quick brown fox jumps over the lazy dog

Then the script could be:

> [POSE_NAME] The quick brown fox jumps over the lazy dog



### Characters

For each character you want to animate, create a *characters.json* file. Change the variable *facesFolder* to be the directory of the character's poses. Set *defaultScale* to be how much the mouth of the character should be scaled up or down.

For each pose the character can do, add the following:

>   "POSE_NAME": [{
>     "image": "POSE_IMAGE.png",
>     "x": POUTH_X_POSITION,
>     "y": MOUTH_Y_POSITION,
>     "scale": HOW MUCH THE MOUTH SHOULD SCALE UP OR DOWN
>   }],

The final pose should not have a comma at the end.

### Mouths

Included in this repo is a mouth pack that I made. The mouth pack is licensed under the same license as the repo. To use your own mouth pack, create a new folder with your mouth images, and duplicate *phonemes.json*, and change the variable *mouthPath* to the path of your mouth pack.

## Usage

### Flags

| Flag | Name        | *** = Required,  * = Recommended | Description                                                  |
| ---- | ----------- | -------------------------------- | ------------------------------------------------------------ |
| -a   | --audio     | ***                              | The path to the audio file being animated                    |
| -t   | --text      | ***                              | The path to the script of the audio file                     |
| -o   | --output    |                                  | The output of the program (output.mp4)                       |
| -s   | --offset    | *                                | How far in advance (in seconds) the program should start animating a word (0.8) |
| -c   | --character | *                                | The list of character poses (character)                      |
| -m   | --mouths    |                                  | The mouth pack and phonemes list (phonemes.json)             |
| -d   | --scale     |                                  | The resolution of the final video (1920:1080)                |



### Windows

Launch anaconda

> python image-generator.py -a audio.mp3 -t text.txt [flags]
