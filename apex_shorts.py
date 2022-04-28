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
    def __init__(self, source='./ingest', destination='./exports', in_point=0, out_point=0, overwrite=False, logo_file='./watermark.png') -> None:
        # source = where to pull files from
        # destination = where to save the final files
        # single_file = only for testing. helps save time from exporting all files in a folder
        # overwrite = re-exports a file and overwrites existing
        # logo_file = transparent PNG that you can use to put on top of your video

        self.watermark = path.normpath(logo_file)
        self.overwrite = overwrite

        self.in_point = in_point
        self.out_point = out_point

        video_formats = ('.mp4', '.mov', '.mkv')

        # prevents errors where export directory doesn't exist
        export_normalized = path.normpath(destination)
        if not path.exists(export_normalized):
            mkdir(export_normalized)

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

            # If it's not the same size, scale it up/down
            if w != 1920 and h != 1080:
                print(f"\nWARNING: Your video dimensions are {w}x{h}. For best results, use clips that are 1920x1080.\n")
                  
            # keep aspect ratio to 9x16, but scale appropriately
            cropped_w = round((h*9)/16)

            # crop the clip based on the calculations above
            cropped_clip = clip.fx(vfx.crop, x_center=w/2 , y_center=h/2, width=cropped_w, height=h)

            # use a copy of the clip imported above
            hb_crop = clip
            # mask it using png
            hb_mask = ImageClip('./mask.png', ismask=True).set_duration(clip.duration).resize(height=h).set_pos((0, 0))
            hb_crop.mask = hb_mask
            # crop it to make it easier to move around. Calculations based on 1920x1080 recording (x_pos / 1920) or (y_pos / 1080)
            hb_crop.fx(
                vfx.crop,
                x1=round(w*0.028125),
                y1=round(h*0.883333),
                x2=round(w*0.228125),
                y2=round(h*0.952778)
            )
            # mute duplicate track
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

            # close the files to clear memory
            final.close()
            cropped_clip.close()
            clip.close()
            hb_mask.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automate the editing of Apex Legends highlights in 9/16 format')

    parser.add_argument('-s', '--source', dest='source', type=str, default='./ingest', help="Directory to scrape for video files")
    parser.add_argument('-d', '--destination', dest='destination', type=str, default='./exports', help="Location to save exported videos")

    parser.add_argument('-i', '--inpoint', dest='inpoint', type=int, default=0, help="Set in point (seconds)")
    parser.add_argument('-o', '--outpoint', dest='outpoint', type=int, default=0, help="Set out point (seconds)")

    parser.add_argument('-r', '--overwrite', action='store_true', dest='overwrite', default=False, help="Overwrite existing files")
    parser.add_argument('-w', '--watermark', dest='watermark', type=str, nargs=1, help="Filepath for logo/watermark file")

    args = parser.parse_args()

    ApexAutoCropper(
        source=args.source,
        destination=args.destination,
        in_point=args.inpoint,
        out_point=args.outpoint,
        overwrite=args.overwrite,
    )
