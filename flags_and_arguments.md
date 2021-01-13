### Flags and Arguments

| Shortcut | Command        | Required | Default           | Type  | Description                                                  |
| -------- | -------------- | -------- | ----------------- | ----- | ------------------------------------------------------------ |
| -a       | --audio        | *        |                   | str   | The path to the audio file being animated                    |
| -t       | --text         | *        |                   | str   | The path to the script of the audio file                     |
| -o       | --output       |          | "output.mp4"      | str   | The output of the program                                    |
| -c       | --character    |          | "characters.json" | str   | The list of character poses                                  |
| -m       | --mouths       |          | "phonemes.json"   | str   | The mouth pack and phonemes list                             |
| -d       | --dimensions   |          | "1920:1080"       | str   | The resolution of the final video                            |
| -v       | --verbose      |          |                   | flag  | Dump process outputs to the shell                            |
|          | --crumple_zone |          |                   | flag  | Add 10 seconds to the end of the video of the character with their mouth shut, in the last pose they were in. Useful for exporting to a video editor while working with another framerate. |
| -s       | --offset       |          | 0                 | float | How many milliseconds to shift the video forward by relative to the audio |
| -r       | --framerate    |          | 100               | int   | NOT CURRENTLY WORKING -framerate of the video                |
