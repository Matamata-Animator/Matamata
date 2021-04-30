### Flags and Arguments

| Shortcut | Command                 | Required | Default                          | Type  | Description                                                  |
| -------- | ----------------------- | -------- | -------------------------------- | ----- | ------------------------------------------------------------ |
| -a       | --audio                 | *        |                                  | str   | The path to the audio file being animated                    |
| -t       | --text                  |          |                                  | str   | The path to the script of the audio file                     |
| -ts      | --timestamps            |          |                                  | str   | The path to the file containing pose  timestamps.            |
| -o       | --output                |          | "output.mp4"                     | str   | The output of the program                                    |
| -c       | --character             |          | "characters.json"                | str   | The list of character poses                                  |
| -m       | --mouths                |          | "phonemes.json"                  | str   | The mouth pack and phonemes list                             |
| -d       | --dimensions            |          | The dimensions of the first pose | str   | The resolution of the final video. Passed in the form, "1920:1080" |
| -ds      | --dimension_scaler      |          | 1                                | float | Scales the final dimensions up or down. The lower this number, the lower res the output will be, but the faster image generation is. |
| -v       | --verbose               |          |                                  | flag  | Dump process outputs to the shell                            |
|          | --crumple_zone          |          |                                  | flag  | Add 10 seconds to the end of the video of the character with their mouth shut, in the last pose they were in. Useful for exporting to a video editor while working with another framerate. |
| -s       | --offset                |          | 0                                | float | How many milliseconds to shift the video forward by relative to the audio |
| -r       | --framerate             |          | 100                              | int   | NOT CURRENTLY WORKING -framerate of the video                |
| -em      | --emotion_detection_env |          |                                  | str   | The name of the environment file to load for emotion detection. Mutually exclusive with `-ts`. More info in the README. |
| -nd      | --no_docker |          |                                  | flag   | Don't start docker automatically |
| -cd      | --codec |          |                                  | str   | The video codec used for the VideoWriter |
