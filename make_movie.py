#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Create a time-lapse movie from a directory of images."""


from __future__ import division
from __future__ import print_function

import argparse
import os
import subprocess
from datetime import datetime
from operator import itemgetter
import collections
from PIL import ExifTags, Image, ImageFont, ImageDraw
from mutagen.mp3 import MP3  # pylint: disable=import-error
from progress.bar import Bar  # pylint: disable=import-error


class MakeMovie:
    """Make a movie using image files."""

    def __init__(self):
        """Get options and start making a movie."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-s",
            "--source_dir",
            dest="source_directory",
            help="Directory containing original images. \
                                  Default to current directory.",
            default=".",
        )
        parser.add_argument(
            "-t",
            "--tmp_dir",
            dest="tmp_directory",
            help="Directory containing temporary images. " "Default to tmp.",
            default="tmp/",
        )
        parser.add_argument(
            "-f",
            "--frame_rate",
            dest="fps",
            help="Frames per second for the output movie. " "Default to 2.",
            default=2,
        )
        parser.add_argument(
            "-o",
            "--output_filename",
            dest="output_filename",
            help="Output filename. Default to movie.",
            default="movie.mkv",
        )
        parser.add_argument(
            "-w",
            "--max_width",
            dest="max_width",
            help="Maximum width of output video. Default to " "1920.",
            default=1920,
        )
        parser.add_argument(
            "-e",
            "--max_height",
            dest="max_height",
            help="Maximum height of output video. Default to " "1080.",
            default=1080,
        )
        parser.add_argument(
            "-m",
            "--music",
            dest="music",
            help="Name of audio file to add to video.",
            default=None,
        )
        parser.add_argument(
            "-k",
            "--skip",
            dest="skip",
            help="Skip scaling images and use existing " "temporary images.",
            default=False,
        )
        options = parser.parse_args()
        fps = options.fps

        image_names = self.get_image_names(options.source_directory)

        size = self.get_max_image_resolution(
            image_names, options.max_width, options.max_height
        )
        print(
            "Found {} images and setting resolution to (w, h) = ({}, {}).".format(
                len(image_names), size[0], size[1]
            )
        )

        if not options.skip:
            self.add_border_to_images(
                image_names, options.source_directory, options.tmp_directory, size
            )

        if options.music is not None:
            audio = MP3(options.music)
            fps = len(image_names) / audio.info.length
            print(
                "Adding soundtrack {}, {}s, {} fps".format(
                    options.music, audio.info.length, fps
                )
            )

        self.make_movie(fps, options.output_filename, options.tmp_directory)
        if options.music is not None:
            self.add_music(options.output_filename, options.music)

    @classmethod
    def save_landscape_images(cls, source_dir, new_image_directory):
        """Save any images that are in landscape mode (width > height)."""
        valid_extensions = ["png", "jpg"]
        for _, _, files in os.walk(source_dir):
            for image in files:
                ext = image[-3:].lower()
                if ext not in valid_extensions:
                    continue

                orig_image = Image.open(source_dir + image)
                size = orig_image.size
                if size[0] >= size[1]:
                    new_name = new_image_directory + os.path.basename(image)
                    print("new_name: {}".format(new_name))
                    orig_image.save(new_name)

    # Consider using a different library to scale the image more quickly:
    # https://github.com/jbaiter/jpegtran-cffi
    # pylint: disable=too-many-locals
    @classmethod
    def add_border_to_images(
        cls, image_list, source_directory, new_image_directory, size
    ):
        """Add border to images to make them all the same size."""
        img_num = 1
        progress = Bar("Processing", max=len(image_list))
        for timestamp, image in image_list.items():
            new_image = Image.new("RGB", size)
            orig_image = Image.open(image)
            width, height = orig_image.size
            # Handle some weirdness with image orientation:
            # https://stackoverflow.com/questions/13872331/rotating-an-image-with-orientation-specified-in-exif-using-python-without-pil-in
            for orientation in ExifTags.TAGS:
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            # pylint: disable=protected-access
            info = dict(orig_image._getexif().items())
            # pylint: enable=protected-access
            if orientation in info:
                if info[orientation] == 3:
                    orig_image = orig_image.transpose(Image.ROTATE_180)
                elif info[orientation] == 6:
                    orig_image = orig_image.transpose(Image.ROTATE_270)
                    width, height = height, width
                elif info[orientation] == 8:
                    orig_image = orig_image.transpose(Image.ROTATE_90)
                    width, height = height, width
            scale_ratio = 1.0
            if width > size[0] or height > size[1]:
                scale_ratio = min(size[0] / width, size[1] / height)
                orig_image = orig_image.resize(
                    ((int(width * scale_ratio)), int(height * scale_ratio)),
                    Image.BICUBIC,
                )
            new_image.paste(
                orig_image,
                (
                    int((size[0] - width * scale_ratio) / 2),
                    int((size[1] - height * scale_ratio) / 2),
                ),
            )
            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 120
            )
            date = datetime.strptime(timestamp, "%Y%m%d")
            date = date.strftime("%B %d, %Y")
            draw.text((100, 940), date, (255, 255, 255), font=font)
            new_name = image[len(source_directory) :]  # NOLINT
            new_name = new_image_directory + "/image_" + str(img_num).zfill(5) + ".jpg"
            new_image.save(new_name)
            img_num += 1
            progress.next()
        progress.finish()

    # pylint: enable=too-many-locals

    @classmethod
    def get_max_image_resolution(
        cls, image_list, absolute_max_width, absolute_max_height
    ):
        """From a list of images find the maximum height and width."""
        max_height = 0
        max_width = 0
        for dummy, image in image_list.items():
            orig_image = Image.open(image)
            orig_size = orig_image.size
            if orig_size[0] > max_width:
                max_width = orig_size[0]
            if orig_size[1] > max_height:
                max_height = orig_size[1]

        if max_width > absolute_max_width:
            max_width = absolute_max_width
        if max_height > absolute_max_height:
            max_height = absolute_max_height

        return [max_width, max_height]

    @classmethod
    def get_image_names(cls, source_dir):
        """Get the filenames of images in a directory."""
        valid_extensions = ["png", "jpg"]
        image_names = {}
        for _, _, files in os.walk(source_dir):
            for filename in files:
                ext = filename[-3:].lower()
                if ext not in valid_extensions:
                    continue

                current_image = Image.open(source_dir + filename)
                # pylint: disable=protected-access
                info = current_image._getexif()
                # pylint: enable=protected-access
                if info is None:
                    print("{} has no metadata information.".format(filename))
                    continue
                if 36867 in info:
                    timestamp = str(info[36867]).replace(":", "")[:-7].upper()
                elif 36868 in info:
                    timestamp = str(info[36868]).replace(":", "")[:-7].upper()
                else:
                    try:
                        timestamp = str(info[306]).replace(":", "")[:-7].upper()
                    except KeyError as exc:
                        print("Exception for {}: {}".format(filename, exc))
                        continue
                image_names[timestamp] = source_dir + filename

        image_names_sorted = collections.OrderedDict(
            sorted(image_names.items(), key=itemgetter(0))
        )
        return image_names_sorted

    @classmethod
    def make_movie(cls, fps, output_filename, img_dir):
        """Create a movie using images in a specified directory."""
        command = (
            "avconv",
            "-r",
            str(fps),
            "-i",
            img_dir + "/image_%05d.jpg",
            "-b:v",
            "1000k",
            output_filename,
        )

        print("\nabout to execute:\n%s\n" % " ".join(command))
        subprocess.check_call(command)

    @classmethod
    def add_music(cls, output_filename, music):
        """Add a song as background music for video.

        To make a longer song I like to merge my kids favorite songs together.
        Instructions at
        http://www.practicatechnical.com/computer-tips/ubuntu-tips/
        how-to-merge-multiple-mp3-files
        were most helpful:

        mp3wrap tmp.mp3 1.mp3 2.mp3 3.mp3
        ffmpeg -i tmp_MP3WRAP.mp3 -acodec copy all.mp3 && rm tmp_MP3WRAP.mp3
        id3cp 1.mp3 all.mp3
        """
        command = (
            "avconv",
            "-i",
            output_filename,
            "-i",
            music,
            "-map",
            "0:0",
            "-map",
            "1:0",
            "-vcodec",
            "copy",
            "-acodec",
            "copy",
            "music-" + output_filename,
        )

        print("\nabout to execute:\n%s\n" % " ".join(command))
        subprocess.check_call(command)


if __name__ == "__main__":
    MakeMovie()
