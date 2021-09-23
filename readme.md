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
     * [Windows](#Windows---Usage)
     * [Ubuntu](#Ubuntu---Usage)
* [Contributing](#Contributing)


## Installation

### Windows

* Install Python 3.8+
  * During the installation select the add to path option
* Install [NodeJS](https://nodejs.org/en/) 14+
  * Make sure to include the optional add-ons

* Install yarn and typescript

```bash
npm install --global yarn typescript
```

* Download the code using git or the button in the top right

```bash
git clone https://github.com/Matamata-Animator/Matamata-Core.git
```

* Open the folder In command prompt and install the dependencies

```
yarn
```

### Ubuntu

* Clone the repo

```shell
git clone https://github.com/AI-Spawn/Auto-Lip-Sync
cd Auto-Lip-Sync
```
* Install required packages

```shell
sudo apt install docker.io nodejs
```
* Install yarn and typescript

```bash
sudo npm install --global yarn typescript
```

* Open the folder in the terminal and install the dependencies

```
yarn
```

### Mac 

* (Not Required for Intel Macs) Install [Anaconda Navigator](https://www.anaconda.com/products/individual)
* Install Homebrew

```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

* Install node, yarn

``` 
brew install node yarn
```

* Download the code using git or the button in the top right

```bash
git clone https://github.com/Matamata-Animator/Matamata-Core.git
```

* Open the folder in the terminal and install the dependencies

```
yarn
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

The easiest way to create the character file is by using the character creator in [Matamata Studio](https://github.com/Matamata-Animator/Matamata-Studio).

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

### Arguments

#### Default Arguments

This covers the most important flags and arguments. For the complete list, go to [Default Arguments](defaults/default_args.json). 

| Shortcut | Command      | Required | Default                    | Type | Description                                       |
| -------- | ------------ | -------- | -------------------------- | ---- | ------------------------------------------------- |
| --a      | --audio      | *        |                            | str  | The path to the audio file being animated         |
| --t      | --timestamps |          |                            | str  | The path to the file containing pose  timestamps. |
| --o      | --output     |          | "defaults/output.mp4"      | str  | The output of the program                         |
| --c      | --character  |          | "defaults/characters.json" | str  | The list of character poses                       |
| --m      | --mouths     |          | "defaults/phonemes.json"   | str  | The mouth pack and phonemes list                  |
| --V      | --verbose    |          | 1                          | int  | Dump process outputs to the shell                 |

#### Custom Defaults

You can set custom default arguments by creating a file `config.json` in the main folder. In this file, the key is the command and the value is what you want the new default to be. For instance, if you wanted to always be set to verbose mode 3, your file will be:

```json
{
	"verbose": 3
}
```

### Windows - Usage

Launch *Docker Desktop*

Launch terminal in the Matamata-Core folder
```
yarn animate --a audio.wav [arguments]
```


### Ubuntu - Usage

Launch Terminal
```
sudo docker run --name gentle -p 8765:8765 lowerquality/gentle &
sudo yarn animate --a audio.wav [arguments]
```



## Contributing

Do you use this project and want to see a new feature added? Open an issue with the tag *feature request* and say what you want.

Want to try your hand at writing code? Create a fork, upload your code, and make a pull request. Anything from fixing formatting/typos to entirely new features is welcome!

Don't know what to work on? Take a look at the issues page to see what improvements people want. Anything marked *good first issue* should be great for newcomers!
