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

> docker run --name gentle -p 8765:8765 lowerquality/gentle
>
> docker kill gentle
>
> docker rm gentle
