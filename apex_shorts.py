#!/usr/bin/python3

from os import listdir, path, mkdir
from sys import exit
from moviepy.editor import *
import argparse

### INSTRUCTIONS ###
# By default, the program will pull all video files from a folder titled "ingest" in the current directory
# files imported must be videos (mov, mp4, etc)
# you can also define your own file locations below by changing the ingest_dir and export_dir variables.

class ApexAutoCropper:
    def __init__(self, source='./ingest', destination='./exports', stretch=False, in_point=0, out_point=0, overwrite=False, hb_enable=True, logo_file='./watermark.png') -> None:
        # source = where to pull files from
        # destination = where to save the final files
        # single_file = only for testing. helps save time from exporting all files in a folder
        # overwrite = re-exports a file and overwrites existing
        # logo_file = transparent PNG that you can use to put on top of your video

        self.watermark = path.normpath(logo_file)
        self.overwrite = overwrite
        self.hb_enable = hb_enable
        self.stretch = stretch

        self.in_point = in_point
        self.out_point = out_point

        video_formats = ('.mp4', '.mov', '.mkv')

        # prevents errors where export directory doesn't exist
        export_normalized = path.normpath(destination)
        if not path.exists(export_normalized):
            mkdir(export_normalized)

        self.mask_dir = path.join(path.dirname(__file__), 'masks')

        if path.isdir(source): # if the source is a directory, loop through files in that folder

            file_list = listdir(source) # get a list of all files in the folder and loop through them
            print(f'Converting {len(file_list)} files')

            for file in file_list:
                if file.endswith(video_formats): # make sure it's a valid video file
                    self.source_path = path.join(path.normpath(source), file)
                    self.export_path = path.join(export_normalized, f'{path.splitext(file)[0]}_SHORTS.mp4')
                    self.crop_video()

        else: # for when the source is just a single file
            filename = path.split(source)[1]
            if filename.endswith(video_formats): # make sure it's a valid video file
                self.source_path = path.normpath(source)
                self.export_path = path.join(export_normalized, f'{path.splitext(filename)[0]}_SHORTS.mp4')
                self.crop_video()

    def crop_video(self):
        if not path.exists(self.export_path) or self.overwrite == True:

            try: # import the clip and normalize it to 0 db
                clip = VideoFileClip(self.source_path).fx(afx.audio_normalize)
            
            except Exception as e: # exception for when clip has no audio.
                print(f'ERROR: {e} (File has no audio to normalize)')
                clip = VideoFileClip(self.source_path)

            if self.out_point == 0 or self.out_point > clip.duration:
                self.out_point = clip.duration
            clip = clip.subclip(self.in_point, self.out_point)

            # get size of the clip (normally 1920x1080)
            w, h = clip.size

            # determine the new width of video to fit 9x16 screens
            cropped_w = round((h*9)/16)

            # crop the clip based on the calculations above
            cropped_clip = clip.fx(vfx.crop, x_center=w/2 , y_center=h/2, width=cropped_w, height=h)
            comp_clip = [cropped_clip]

            # if hb_enable is true, include masked health bar
            if self.hb_enable:
                # use a copy of the clip imported above
                hb_crop = clip
              
                if self.stretch: # for 16x10 apsect ratios recorded at 1920x1080 (has black bars on side)
                    mask_path = path.join(self.mask_dir, '1080p_16x10_v2.png')
                    position = (-40, -1020)
 
                else: # for 1080p 16x9 videos
                    mask_path = path.join(self.mask_dir, '1080p_16x9.png')
                    position = (50, -1010)

                hb_mask = ImageClip(mask_path, ismask=True).set_duration(clip.duration).resize(height=h, width=w).set_pos((0, 0))
                hb_crop.mask = hb_mask
                hb_crop.volumex(0) # mute duplicate track

                comp_clip.append(hb_crop.set_position(position).resize(1.10))

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

                comp_clip.append(logo)

            final = CompositeVideoClip(comp_clip)

            # and export it
            final.write_videofile(self.export_path, codec='libx264', audio_codec='aac', remove_temp=True, preset='slow')

            # close the files to clear memory
            final.close()
            clip.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automate the editing of Apex Legends highlights in 9/16 format')

    parser.add_argument('-s', '--source', dest='source', type=str, default='./ingest', help="Directory to scrape for video files")
    parser.add_argument('-d', '--destination', dest='destination', type=str, default='./exports', help="Location to save exported videos")

    parser.add_argument('-i', '--inpoint', dest='inpoint', type=int, default=0, help="Set in point (seconds)")
    parser.add_argument('-o', '--outpoint', dest='outpoint', type=int, default=0, help="Set out point (seconds)")

    parser.add_argument('-r', '--overwrite', action='store_true', dest='overwrite', default=False, help="Overwrite existing files")
    parser.add_argument('-b', '--hidehealthbar', action='store_false', dest='hb_enable', default=True, help="Disables Health Bar overlay")
    parser.add_argument('-w', '--watermark', dest='watermark', type=str, nargs=1, help="Filepath for logo/watermark file")
    parser.add_argument('--stretch', dest='stretch', action='store_true', default=False, help="Enables 16x10 aspect ratios")

    args = parser.parse_args()

    try:
        ApexAutoCropper(
            source=args.source,
            destination=args.destination,
            in_point=args.inpoint,
            out_point=args.outpoint,
            stretch=args.stretch,
            overwrite=args.overwrite,
            hb_enable=args.hb_enable
        )

    except Exception as e:
        exit(f'\nEXITING: {e}')
