# Auto Lip Sync

This is the auto-lip-sync tool created by AI Spawn.

## Table of Contents



* [Table of Contents](#table-of-contents)
* [Installation](#Installation)
     * [Windows](#Windows)
     * [Ubuntu](#Ubuntu---Untested)
     * [Mac](#Mac---Untested)
* [Setup](#setup)
     * [Script](#script)
     * [Characters](#characters)
     * [Mouths](#mouths)
* [Usage](#usage)
     * [Flags and Arguments](#flags-and-arguments)
     * [Windows](#Windows)
     * [Ubuntu](#Ubuntu)
     * [Mac](#Mac)
* [Contributing](#Contributing)


## Installation

### Windows

This tool was made to be more convenient for people, and since the majority of people, including me, only use Windows on a daily basis, it was essential for this to be able to run on Windows. That being said, there are a few external programs required to make this run.

Install:
* [Docker Desktop](https://www.docker.com/get-started)
* [Anaconda](https://www.anaconda.com/products/individual#Downloads), or a similar python environment that allows you to use pip. This is  just the one I recommend.



Download this repo and open Anaconda Prompt in the folder. If you have Git installed, that can be done via:

> git clone https://github.com/AI-Spawn/Auto-Lip-Sync
>
> cd Auto-Lip-Sync

Otherwise, use the download button on GitHub, extract files from the zip, and open Anaconda Prompt in that folder.



Install required packages

> pip install -r requirements.txt
>
> conda install ffmpeg

Launch Docker if it isn't launched already

> docker pull lowerquality/gentle

### Ubuntu - Untested

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

Download [Anaconda](https://www.anaconda.com/products/individual#Downloads)

Download this repo:

> git clone https://github.com/AI-Spawn/Auto-Lip-Sync

Open the anaconda prompt in the Auto-Lip-Sync folder.



Install required packages

> pip install -r requirements.txt
>
> conda install ffmpeg

Launch Docker if it isn't launched already



Pull lowerquality/gentle from DockerHub:

> docker pull lowerquality/gentle



## Setup

### Script

The script should be a text document with a transcript of audio, and poses in-between brackets. For instance, if the audio read:

> The quick brown fox jumps over the lazy dog

Then the script could be:

> [POSE_NAME] The quick brown fox jumps over the lazy dog



### Characters

For an example of a character file, refer to *characters.json*

For each pose you want to animate, create a duplicate of *characters.json*. Change the variable *facesFolder* to be the directory of the character's poses. Set *defaultScale* to be how much the mouth images of the character should be scaled up or down.

For each pose the character can do, add the following:

>   "POSE_NAME": {
>    "image": "POSE_IMAGE.png",
>    "x": POUTH_X_POSITION,
>    "y": MOUTH_Y_POSITION,
>    "scale": HOW MUCH THE MOUTH SHOULD SCALE UP OR DOWN,
>   "facingLeft": OPTIONAL -- True if character is looking to the left
>
>   },

The final pose should not have a comma at the end.

### Mouths

Included in this repo is a mouth pack that I made. The mouth pack is licensed under the same license as the repo. To use your own mouth pack, create a new folder with your mouth images, and duplicate *phonemes.json*, and change the variable *mouthPath* to the path of your mouth pack.

More advance users can edit or create their own *phonemes*.json, however that is significantly more difficult and probably not worth it. Replacing the mouth images is a significantly simpler solution.

## Usage

### Flags and Arguments

This covers the most important flags and arguments. For the complete list, go to [Flags and Arguments](flags_and_arguments.md). 

| Shortcut | Command        | Required | Default           | Type | Description                                                  |
| -------- | -------------- | -------- | ----------------- | ---- | ------------------------------------------------------------ |
| -a       | --audio        | *        |                   | str  | The path to the audio file being animated                    |
| -t       | --text         | *        |                   | str  | The path to the script of the audio file                     |
| -o       | --output       |          | "output.mp4"      | str  | The output of the program                                    |
| -c       | --character    |          | "characters.json" | str  | The list of character poses                                  |
| -m       | --mouths       |          | "phonemes.json"   | str  | The mouth pack and phonemes list                             |
| -d       | --dimensions   |          | "1920:1080"       | str  | The resolution of the final video                            |
| -v       | --verbose      |          |                   | flag | Dump process outputs to the shell                            |
|          | --crumple_zone |          |                   | flag | Add 10 seconds to the end of the video of the character with their mouth shut, in the last pose they were in. Useful for exporting to a video editor while working with another framerate. |



### Windows

Launch *Docker Desktop*

Launch *Anaconda Prompt*

> python animate.py -a audio.mp3 -t text.txt [flags]



### Ubuntu

Launch Terminal

> sudo python animate.py -a audio.mp3 -t text.txt [flags]



### Mac

Launch *Docker Desktop*

Launch *Anaconda Prompt*

> python animate.py -a audio.mp3 -t text.txt [flags]

This may need to be accompanied by a *sudo* beforehand.



## Contributing

Do you use this project and want to see a new feature added? Open an issue with the tag *feature request* and say what you want.

Want to try your hand writing code? Create a fork, upload your code, and make a pull request. Anything from fixing formatting/typos to entirely new features is welcome!

Don't know what to work on? Take a look at the issues page to see what improvements people want. Anything marked *good first issue* should be great for newcomers!
