# Auto Lip Sync

This is the auto-lip-sync tool created by AI Spawn.

## Installation

### Windows

This tool was made to be more convenient for people, and since the majority of people, including me, only use Windows on a daily basis, it was essential for this to be able to run on Windows. That being said, there are a few external programs required to make this run.

Install:

* [Docker Desktop](https://www.docker.com/get-started)
* [Anaconda](https://www.anaconda.com/products/individual), or a similar python environment that allows you to use pip. This is  just the one I recommend.



Download this repo and open Anaconda Prompt in the folder. If you have Git installed, that can be done via:

> git clone https://github.com/AI-Spawn/Auto-Lip-Sync
>
> cd Auto-Lip-Sync

Otherwise, use the download button on Github, extract files from the zip, and open Anaconda Prompt in that folder.



Install required packages

> pip install -r requirements.txt
>
> conda install ffmpeg

Launch Docker if it isn't launched already

> docker pull lowerquality/gentle

### Linux (Ubuntu) - Untested

Install docker

> sudo apt-get update



> sudo apt-get install \
>     apt-transport-https \
>     ca-certificates \
>     curl \
>     gnupg-agent \
>     software-properties-common



> curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -



**Add the docker repo to your system:**

On *x86_64 / amd64*:

> ```
> sudo add-apt-repository \
>    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
>    $(lsb_release -cs) \
>    stable"
> ```

On *armhf*:

> ```
> sudo add-apt-repository \
>    "deb [arch=armhf] https://download.docker.com/linux/ubuntu \
>    $(lsb_release -cs) \
>    stable"
> ```

On *arm64*:

> ```
> sudo add-apt-repository \
>    "deb [arch=arm64] https://download.docker.com/linux/ubuntu \
>    $(lsb_release -cs) \
>    stable"
> ```

**Install the engine**:

> ```
> sudo apt-get update
> sudo apt-get install docker-ce docker-ce-cli containerd.io
> ```

Verify Docker's installation

> ```
> sudo docker run hello-world
> ```

Clone the repo

> git clone https://github.com/AI-Spawn/Auto-Lip-Sync
>
> cd Auto-Lip-Sync

Install required packages

> pip install -r requirements.txt
>
> sudo apt install ffmpeg

Pull the lowerquality/gentle container

> docker pull lowerquality/gentle

### Mac - Untested

Download [Docker Desktop for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac/)



## Setup

### Recording

This tool works best when you talk at a constant pace. It also works best when your audio is clear, so speak clearly, consistently, and I recommend using a program like [audacity](https://www.audacityteam.org/download/) (free).

### Script

The script should be a text document with a transcript of audio, and poses in-between brackets. For instance, if the audio read:

> The quick brown fox jumps over the lazy dog

Then the script could be:

> [POSE_NAME] The quick brown fox jumps over the lazy dog



### Characters

For an example of a character file, refer to *characters.json*

For each character you want to animate, create a duplicate of *characters.json*. Change the variable *facesFolder* to be the directory of the character's poses. Set *defaultScale* to be how much the mouth of the character should be scaled up or down.

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

More advance users can edit or create their own *phonemes*.json, however that is significantly more difficult and probably not worth it. Replacing the mouth images is a significantly simpler solution.

## Usage

### Flags

| Flag | Shortcut       | *** = Required,  * = Recommended | Description                                                  |
| ---- | -------------- | -------------------------------- | ------------------------------------------------------------ |
| -a   | --audio        | ***                              | The path to the audio file being animated                    |
| -t   | --text         | ***                              | The path to the script of the audio file                     |
| -o   | --output       |                                  | The output of the program ("output.mp4")                     |
| -s   | --offset       | *                                | How far in advance (in seconds) the program should start animating a word (0.8) |
| -c   | --character    | *                                | The list of character poses ("character")                    |
| -m   | --mouths       |                                  | The mouth pack and phonemes list ("phonemes.json")           |
| -d   | --scale        |                                  | The resolution of the final video ("1920:1080")              |
| -v   | --verbose      |                                  | Dump process outputs to the shell (False)                    |
| -l   | --skipframes   |                                  | Whether phonemes should be skipped if the phoneme length doesn't meet the frame threshold (True) |
| -t   | --skipthreshold |                                  | The amount of time (in frames) a phoneme needs to take up for it to be displayed (1) |
| -r   | --framerate    |                                  | The framerate of the animation (25)                          |



### Windows

Launch *Docker Desktop*

Launch Anaconda Prompt

> python animate.py -a audio.mp3 -t text.txt [flags]



### Linux (Ubuntu)

Launch Terminal

> python animate.py -a audio.mp3 -t text.txt [flags]

This may need to be accompanied by a *sudo* beforehand.



### Mac

Launch *Docker Desktop*

Launch Terminal

> python animate.py -a audio.mp3 -t text.txt [flags]

This may need to be accompanied by a *sudo* beforehand.



## Contributing

Do you use this project and want to see a new feature added? Open an issue with the tag *feature request* and say what you want.

Want to try your hand writing code? Create a fork, upload your code, and make a pull request. Anything from fixing formatting/typos to entirely new features is welcome!

Don't know what to work on? Take a look at the issues page to see what improvements people want. Anything marked *good first issue* should be great for newcomers!
