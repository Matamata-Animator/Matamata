[<img title="" src="https://aispawn.com/support/readme-image.png" alt="Support Me" width="168">](https://aispawn.com/support)

# Matamata Animator

Matamata (an acronym for "Matamata attempts to animate mouths, at times accurately") is a tool to automatically create lip-synced animations.

<img src="https://raw.githubusercontent.com/Matamata-Animator/Branding/main/Logos-Icons/logo.png" title="" alt="logo" width="185">

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Installation](#Installation)
  - [Mac](#Mac)
  - [Windows](#Windows)
  - [Linux](#Linux)
- [Setup](#Setup)
  - [Character File](#character-file)
  - [Timestamps](#timestamps)
  - [Mouths](#mouths)
- [Usage](#Usage)
  - [Flags and Arguments](#flags-and-arguments)
  - [Custom Defaults](#Custom-Defaults)
  - [Running](#Running)
- [Contributing](#Contributing)

## Installation

### Mac

- Install FFmpeg to the path. The easiest way to do this is install [Homebrew]("https://brew.sh/")
  
  ```zsh
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```
  ```
  
  ```zsh
  brew install ffmpeg
  ```

- Download the [Gentle executable](https://github.com/lowerquality/gentle/releases/download/0.11.0/gentle-0.11.0.dmg)

- Download the latest Mac (Darwin) binary from the [releases](https://github.com/Matamata-Animator/Matamata-Core/releases) page

### Windows

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Install Gentle

```cmd
docker pull lowerquality/gentle
```

- Install FFmpeg to the path. You can follow [these](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) instructions.
- Download the latest Windows binary from the [releases](https://github.com/Matamata-Animator/Matamata-Core/releases) page

### Linux

- Install Docker

```shell
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- Install Gentle

```shell
docker pull lowerquality/gentle
```

- Install FFmpeg

```shell
sudo apt update
sudo apt install ffmpeg
```

- Download the latest Linux binary from the [releases](https://github.com/Matamata-Animator/Matamata-Core/releases) page

## Setup

### Character Folder

See [/defaults/SampleCharacter](https://github.com/Matamata-Animator/Matamata-Core/tree/main/defaults/SampleCharacter) for an example of how to create your character folder. 

**A tool for automatically generating this folder is coming soon**

```json
{
  "schema": 5,
  "poses": {
    "defaultMouthScale": 2.0,
    "defaultPose": "purple",
    "purple": {
      "image": "purple.png",
      "x": 640,
      "y": 400,
      "facingLeft": false,
      "mouthScale": 1.0
    },
    "green": {
      "image": "green.png",
      "x": 640,
      "y": 400,
      "facingLeft": false,
      "mouthScale": 1.0
    },
    "blue": {
      "image": "blue.png",
      "x": 640,
      "y": 400,
      "facingLeft": false,
      "mouthScale": 1.0
    }
  },
  "eyes": {
    "scale": 0.8,
    "x": 640,
    "y": 300,
    "images": {
      "angry": "angry.png",
      "normal": "normal.png",
      "sad": "sad.png"
    }
  }
}
```

`poses` contains the images that the character can do

`poses.default_mouth_scale` says how much the mouth should be scaled up or down. `poses.POSE.mouth_scale` is the same thing for a specific pose. These values are multiplied

`x` and `y` are the coordinates on the photo where the mouth should be placed.

`facingLeft` indicates whether to mirror the mouth image. 

`eyes` specifies a "placeable part". The sample character pose images don't have eyes, as these are specified by placeable parts. Although this example has placeable eyes, you can have placeable pins, objects in the background, or even hats.  `scale` specifies how much the placeable part image should be scaled up or down. `x` and `y` specify the location on the pose where the part should be placed. `images` contained key-value pairs where the key is the name of the part, and the value is the image name. This section shows angry, normal, and sad eye selections.

All pose images are in `CharacterFolder/poses`

All placeable part images are in `CharacterFolder/PART_NAME`

### Timestamps

The timestamps file is composed of a list of pose changes along with how many milliseconds into the animation the pose should change. For instance, if you wanted to swap to the `happy` pose after 3.5 seconds, the timestamps file will look like:

> 3500 happy

Additionally, you can change a placeable part by adding the type afterwards.

> 0 angry eyes

You can also remove a placeable part by using the name `None`

> 5000 None eyes

## Usage

### Arguments

| Flag         | Description                                                                                                                                                                   | Default                                          |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| -a           | The path to the audio file being animated (**REQUIRED**)                                                                                                                      |                                                  |
| -k           | OpenAI API Key (**REQUIRED IF `api_url` IS NOT SET**)                                                                                                                         |                                                  |
| -c           | Path to the character folder                                                                                                                                                  | By default, the sample character is used         |
| -o           | Path of the output file                                                                                                                                                       | output.mov                                       |
| -t           | Path to the timestamps file                                                                                                                                                   | "defaults/characters.json"                       |
| -v           | How verbose to be (0 to 3).                                                                                                                                                   | 1                                                |
| -api_url     | URL for the transcription API. By default, this points to OpenAI's Whisper. You can also set it to point to a [LocalAI](https://localai.io/basics/getting_started/) instance. | https://api.openai.com/v1/                       |
| -aligner_url | URL for Gentle Aligner server.                                                                                                                                                | http://localhost:8765/transcriptions?async=false |
| -phonemes    | Custom phonemes JSON path                                                                                                                                                     | By default, the sample phonemes is used          |

#### Custom Defaults

After running the program once, a `defaultArguments.json` file is created in your cache directory (the path to this file is printed at the start of the program running). I recommend storing your API key there. 

### Running

- Launch Gentle
  - Mac: Launch the prebuilt app
  - Windows/Linux: `docker run --name gentle -p 8765:8765 lowerquality/gentle`

```shell
./matamata -a audio.wav [optional arguments]
```

## Contributing

Do you use this project and want to see a new feature added? Open an issue with the tag *feature request* and say what you want.

Want to try your hand at writing code? Create a fork, upload your code, and make a pull request. Anything from fixing formatting/typos to entirely new features is welcome!

Don't know what to work on? Take a look at the issues page to see what improvements people want. Anything marked *good first issue* should be great for newcomers!
