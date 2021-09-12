# Matamata Core

Matamata (an acronym for "Matamata attempts to animate mouths, at times accurately") is a tool to automatically create lip-synced animations. 

<img src="https://raw.githubusercontent.com/Matamata-Animator/Branding/main/Logos-Icons/logo.png" alt="logo" width="200" height="200"/>

## Table of Contents



* [Table of Contents](#table-of-contents)
* [Installation](#Installation)
     * [Windows](#Windows)
     * [Ubuntu](#Ubuntu)
* [Setup](#setup)
     * [Timestamps](#timestamps)
     * [Script](#script)
     * [Characters](#characters)
     * [Mouths](#mouths)
* [Usage](#usage)
     * [Flags and Arguments](#flags-and-arguments)
     * [Additional Features](#Emotion-Detection)
     * [Windows](#Windows---Usage)
     * [Ubuntu](#Ubuntu---Usage)
* [Contributing](#Contributing)


## Installation

### Windows

* Install [Docker Desktop](https://www.docker.com/get-started)
* Launch Docker Desktop if it isn't already running
* Pull the Gentle container:

```bash
docker pull lowerquality/gentle
```
* Install [NodeJS](https://nodejs.org/en/) 14+
  * Make sure to include the optional addons
* Install yarn

```bash
npm install --global yarn
```

* Download the code using git or the button in the top right

```bash
git clone https://github.com/Matamata-Animator/Matamata-Core.git
```

* Open the folder and install the dependencies

```
yarn
```

* Install Vosk model through the [Vosk website](https://alphacephei.com/vosk/models) or using the automatic tool. **This is a 1.6 GB file and thus will take some time, please have patience.**

```bash
yarn downloadModel
```

### Ubuntu

Clone the repo
```
git clone https://github.com/AI-Spawn/Auto-Lip-Sync
cd Auto-Lip-Sync
```
Install required packages
```
sudo apt install ffmpeg python3-pip python3-opencv docker.io
sudo pip3 install -r requirements.txt
```
Pull the lowerquality/gentle container
```
sudo docker pull lowerquality/gentle
```

## Setup

### Timestamps

The timestamps file is composed of a list of pose changes along with how many milliseconds into the animation the pose should change. For instance, if you wanted to swap to the `happy` pose after 3.5 seconds, the timestamps file will look like:

> 3500 happy

### Script

 If no script is provided, the program will automatically generate a script for you. 

The script should be a text document with a transcript of audio, and poses in-between brackets. For instance, if the audio read:

> The quick brown fox jumps over the lazy dog

Then the script could be:

> [POSE_NAME] The quick brown fox jumps over the lazy dog

If poses are provided via a timestamps file, then no poses will be read from the script. 



### Characters

The easiest way to create the character file is by using  the character creator in [Matamata Studio](https://github.com/Matamata-Animator/Matamata-Studio).

~~Alternatively, you can use the [online character creator](https://matamata.aispawn.com/Character-Creator/) tool (DEPRECATED)~~

If you decide to create one manually, for an example of a character file, refer to *characters.json* as an example.

For each pose you want to animate, create a duplicate of *characters.json*. Change the variable *facesFolder* to be the directory of the character's poses. Set *defaultScale* to be how much the mouth images of the character should be scaled up or down.

For each pose the character can do, add the following:

> "POSE_NAME": {
> 
> "image": "POSE_IMAGE.png",
> 
>  "x": MOUTH_X_POSITION,
> 
> "y": MOUTH_Y_POSITION,
> 
>  "scale": HOW MUCH THE MOUTH SHOULD SCALE UP OR DOWN,
>  
>  "facingLeft": OPTIONAL -- True if character is looking to the left,
> 
>   "closed_mouth": OPTIONAL -- the name of the image in your mouths folder used as a closed mouth instead of the default 
> 
>   },

The final pose should not have a comma at the end.

### Mouths

Included in this repo is a mouth pack that I made. The mouth pack is licensed under the same license as the repo. To use your own mouth pack, create a new folder with your mouth images, and duplicate *phonemes.json*, and change the variable *mouthPath* to the path of your mouth pack.

More advance users can edit or create their own *phonemes*.json, however that is significantly more difficult and probably not worth it. Replacing the mouth images is a significantly simpler solution.

## Usage

### Flags and Arguments

Any flags/arguments can be used every time by creating a config file (`config.txt`will be loaded by default if it exists)

This covers the most important flags and arguments. For the complete list, go to [Default Arguments](defaults/default_args.json). 



| Shortcut | Command      | Required | Default                    | Type | Description                                       |
| -------- | ------------ | -------- | -------------------------- | ---- | ------------------------------------------------- |
| --a      | --audio      | *        |                            | str  | The path to the audio file being animated         |
| --t      | --timestamps |          |                            | str  | The path to the file containing pose  timestamps. |
| --o      | --output     |          | "defaults/output.mp4"      | str  | The output of the program                         |
| --c      | --character  |          | "defaults/characters.json" | str  | The list of character poses                       |
| --m      | --mouths     |          | "defaults/phonemes.json"   | str  | The mouth pack and phonemes list                  |
| --V      | --verbose    |          | 1                          | int  | Dump process outputs to the shell                 |



### Windows - Usage

Launch *Docker Desktop*

Launch terminal in the Matamata-Core folder
```
python animate.py -a audio.wav [flags]
```


### Ubuntu - Usage

Launch Terminal
```
sudo python3 animate.py -a audio.wav --codec FMP4 [flags]
```


### Mac

Launch *Docker Desktop*

Launch *Anaconda Prompt*
```
python animate.py -a audio.wav [flags]
```
This may need to be accompanied by a *sudo* beforehand.



## Contributing

Do you use this project and want to see a new feature added? Open an issue with the tag *feature request* and say what you want.

Want to try your hand at writing code? Create a fork, upload your code, and make a pull request. Anything from fixing formatting/typos to entirely new features is welcome!

Don't know what to work on? Take a look at the issues page to see what improvements people want. Anything marked *good first issue* should be great for newcomers!
