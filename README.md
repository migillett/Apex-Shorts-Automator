# Apex-Shorts-Automator
This script automates the adapting Apex Legends game highlights from 1920x1080 landscape to portrait for easy sharing on YouTube Shorts, TikTok, Instagram, etc.

This program loops through all the files in a folder, masks out the player's health bar, moves it to the top of the frame, crops the footage to a 9 by 16 aspect ratio, adds an optional logo, and exports it to an H.264 format.

## Dependencies
This program runs on [Python 3](https://www.python.org/downloads/) and only requires one non-included library: [moviepy](https://pypi.org/project/moviepy/). To install moviepy, just run `pip install moviepy` in your terminal or `pip install -r requirements.txt`.

## Examples
Here are some examples of how the input and output formats of the program. The footage used below is a 1920x1080 60p quicktime file captured using OBS. I recommend using the replay capture, as it can automatically create clips that are specific lengths (30, 60, 90 seconds).

### Before
![before](https://user-images.githubusercontent.com/51103663/162653389-00a93c8a-07b9-44ae-852b-9243ee56e7dd.jpg)

### After
![after](https://user-images.githubusercontent.com/51103663/162654349-2ea55cf4-d1ec-4352-9116-41e747c81cd2.jpg)

## How to Use
You can import this program into another script or run it directly from the command line. For example:

`python3 ./apex_shorts.py -s './ingest/test.mp4' -d './exports' -r -i 3 -o 10`

`-s` or `--source`    The source directory (where all of our game recordings are)

`-d` or `--destination`    The export directory (where you want to export the edited files)

`-i` or `--inpoint`     When you want the video to start (in seconds)

`-o` or `--outpoint`    When you want the video to end (in seconds)

`-r` or `--overwrite` Allows you to overwrite files in case you encounter any exporting errors

`-w` or `--watermark` Allows you to specify a specific filepath for your watermark

## Notes
For best results, use a 500 x 500 pixel transparent PNG for your watermark.

This program has not been tested using footage that is not 1920x1080. If you use alternative aspect ratios, your mileage may vary.
