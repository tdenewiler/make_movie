#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Rename images.

In a directory containing images rename the files to use the format of
IMG_<YYYYMMDD>_<HHMMSSSS>.<ext>. Get the date and time from image metadata. Tested
specifically with HTC One (M8) that uses numbers instead of date in filenames.
"""


from argparse import ArgumentParser
import os
from shutil import copyfile
from PIL import Image


class RenameFileWithDateTime:
    """Rename image files with date and time for easier sorting."""

    def __init__(self):
        """Rename file."""
        parser = ArgumentParser()
        parser.add_argument(
            "-s",
            "--source_dir",
            dest="source_directory",
            help="Directory containing original images. "
            "Default to current directory.",
            default=".",
        )
        parser.add_argument(
            "-t",
            "--tmp_dir",
            dest="tmp_directory",
            help="Directory containing temporary images. " "Default to tmp.",
            default="tmp",
        )
        options = parser.parse_args()
        source_dir = options.source_directory
        new_image_directory = options.tmp_directory
        num_files = len(
            [name for name in os.listdir(source_dir) if os.path.isfile(name)]
        )

        if num_files > 0:
            self.create_files(source_dir, new_image_directory)
        else:
            print(f"No files in {source_dir}")

    def create_files(self, source_dir, tmp_dir):
        """Create the files using metadata."""
        valid_extensions = ["png", "jpg"]
        for _, _, files in os.walk(source_dir):
            for filename in files:
                ext = filename[-3:].lower()
                if ext not in valid_extensions:
                    continue
                self.create_file(filename, source_dir, tmp_dir)

    @classmethod
    def create_file(cls, filename, source_dir, tmp_dir):
        """Create individaul files using metadata."""
        print(f"Opening {filename}")
        if os.path.isfile(source_dir + filename):
            current_image = Image.open(source_dir + filename)
            # pylint: disable=W0212
            info = current_image._getexif()
            # pylint: enable=W0212
            if 36867 in info:
                if info[272] == "HTC6525LVW":
                    print(f"info[36867] = {info[36867]}")
                    new_filename = str(info[36867]).replace(":", "").upper()
                    new_filename = new_filename.replace(" ", "_")
                else:
                    new_filename = (
                        str(info[36867]).replace(":", "")[:-7].upper()
                        + "_"
                        + str(info[36867]).replace(":", "")[9:16].upper()
                    )
            else:
                new_filename = str(info[306]).replace(":", "")[:-7].upper()
            new_filename = tmp_dir + "/" + "IMG_" + new_filename + ".jpg"
            print(f"Original filename = {filename}, new filename = {new_filename}")
            try:
                copyfile(source_dir + "/" + filename, new_filename)
            except IOError:
                print(f"Exception renaming {filename} to {new_filename}")
        else:
            print("{filename} is not a file, skipping.")
        print("*****")


if __name__ == "__main__":
    RenameFileWithDateTime()
