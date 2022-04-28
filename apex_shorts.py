#!/usr/bin/python3

from os import listdir, path, mkdir
from sys import exit
from moviepy.editor import *
import argparse

### INSTRUCTIONS ###
# By default, the program will pull all video files from a folder titled "ingest" in the current directory
# files imported must be videos (mov, mp4, etc)
# you can also define your own file locations below by changing the ingest_dir and export_dir variables.

parser = argparse.ArgumentParser(description='Automate the editing of Apex Legends highlights in 9/16 format')
parser.add_argument('-i', '--ingest', dest='ingest', type=str, nargs=1, help="Where to pull video files from")
parser.add_argument('-e', '--export', dest='export', type=str, nargs=1, help="Where to save exported videos")
parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite', default=False, help="Overwrite existing files")
parser.add_argument('-w', '--watermark', dest='watermark', type=str, nargs=1, help="Filepath for logo/watermark file")
args = parser.parse_args()


class ApexAutoCropper:
    def __init__(self, ingest_dir='./ingest', export_dir='./exports', single_file=False, overwrite=False, logo_file='./watermark.png') -> None:
        # ingest_dir = where to pull files from
        # export_dir = where to save the final files
        # single_file = only for testing. helps save time from exporting all files in a folder
        # overwrite = re-exports a file and overwrites existing
        # logo_file = transparent PNG that you can use to put on top of your video

        self.watermark = path.normpath(logo_file)

        self.overwrite = overwrite
        print(f'Overwrite is set to {self.overwrite}')

        self.ingest = path.normpath(ingest_dir)
        self.export = path.normpath(export_dir)

        self.ingest_path = ''
        self.export_path = ''

        print(f'Ingest Directory: {ingest_dir}')
        print(f'Export Directory: {self.export}')

        # prevents errors where export directory doesn't exist
        if not path.exists(self.export):
            mkdir(self.export)

        # get a list of all files in the folder and loop through them
        file_list = listdir(ingest_dir)
        print(f'Converting {len(file_list)} files')

        for file in file_list:
            if file.endswith(('.mp4', '.mov')): # make sure it's a valid video file
                self.ingest_path = path.join(self.ingest, file)
                self.export_path = path.join(self.export, f'{path.splitext(file)[0]}_SHORTS.mp4')

                if not path.exists(self.export_path):
                    self.crop_video()
                elif self.overwrite:
                    self.crop_video()

                # Break the loop for testing purposes (default is False)
                if single_file: 
                    break

    def crop_video(self):
        # import the clip and normalize it to 0 db
        clip = VideoFileClip(self.ingest_path).fx(afx.audio_normalize)

        # get size of the clip (normally 1920x1080)
        w, h = clip.size
        # keep aspect ratio to 9*16, but scale appropriately
        cropped_height = round((h*9)/16) 

        # crop the clip based on the calculations above
        cropped_clip = clip.fx(vfx.crop, x_center=w/2 , y_center=h/2, width=cropped_height, height=h)

        # use a copy of the clip imported above
        hb_crop = clip
        # mask it using png
        hb_crop.mask = ImageClip('./mask.png', ismask=True).set_duration(clip.duration)
        # crop it to make it easier to move around. Calculations based on 1920x1080 recording (x_pos / 1920) or (y_pos / 1080)
        hb_crop.fx(
            vfx.crop,
            x1=round(w*0.028125),
            y1=round(h*0.883333),
            x2=round(w*0.228125),
            y2=round(h*0.952778)
        )
        # mute track
        hb_crop.volumex(0)

        # if watermark image exists, include in export
        if path.exists(self.watermark):
            # determine margins for logo watermark and health bar (should be close to 40 pixels)
            margins = int(round(h*0.025)+18)

            # create the watermark using transparent png file
            logo = (
                ImageClip(self.watermark)
                .resize(height=h/10)
                .set_duration(clip.duration)
                .margin(right=margins, bottom=margins, opacity=0)
                .set_pos(("right", "bottom")))

            final = CompositeVideoClip([cropped_clip, logo, hb_crop.set_position((59, -802))])

        # otherwise, just export video with cropped health bar
        else:
            final = CompositeVideoClip([cropped_clip, hb_crop.set_position((59, -802))])

        # and export it
        final.write_videofile(self.export_path)


if __name__ == '__main__':
    try:
        ingest = args.ingest[0]
    except TypeError:
        ingest = str(input('\nInput ingest directory: '))

    try:
        export = args.export[0]
    except TypeError:
        export = str(input('\nInput export directory: '))

    try:
        print(args.overwrite)
        ApexAutoCropper(
            ingest_dir=ingest,
            export_dir=export,
            overwrite=args.overwrite
        )
    except Exception as e:
        exit(e)
