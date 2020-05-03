#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Resize an image."""

from argparse import ArgumentParser
from PIL import Image


class TestResizeImage:  # pylint: disable=too-few-public-methods
    """Resize images."""

    def __init__(self):
        """Resize images."""
        parser = ArgumentParser()
        parser.add_argument(
            "-i",
            "--input_filename",
            dest="input_filename",
            help="Input filename. Default to empty.",
            default="",
        )
        parser.add_argument(
            "-o",
            "--output_filename",
            dest="output_filename",
            help="Output filename. Default to movie.",
            default="movie",
        )
        options = parser.parse_args()
        image_max_width = 1920
        image_max_height = 1280

        self.resize_image(
            options.input_filename,
            options.output_filename,
            image_max_width,
            image_max_height,
        )

    @classmethod
    def resize_image(cls, input_filename, output_filename, max_width, max_height):
        """Resize an image."""
        print("Resizing {}".format(input_filename))
        orig_image = Image.open(input_filename)
        orig_size = orig_image.size
        new_size = (max_width, max_height)
        new_image = Image.new("RGB", new_size)
        if orig_size[0] > max_width or orig_size[1] > max_height:
            print(
                "Original size is ({}, {}) and max size is ({}, {})".format(
                    orig_size[0], orig_size[1], max_width, max_height
                )
            )
            w_ratio = max_width / orig_size[0]
            h_ratio = max_height / orig_size[1]
            scale_ratio = min(w_ratio, h_ratio)
            print(
                "Resized {} using ratio of {} since w_ratio = {} and "
                "h_ratio = {}".format(input_filename, scale_ratio, w_ratio, h_ratio)
            )
            orig_image = orig_image.resize(
                ((int(orig_size[0] * scale_ratio)), int(orig_size[1] * scale_ratio)),
                Image.ANTIALIAS,
            )
            print(
                "orig_image is now ({}, {})".format(
                    int(orig_size[0] * scale_ratio), int(orig_size[1] * scale_ratio)
                )
            )
        new_image.paste(
            orig_image,
            (
                int((new_size[0] - orig_size[0] * scale_ratio) / 2),
                int((new_size[1] - orig_size[1] * scale_ratio) / 2),
            ),
        )
        new_image.save(output_filename)


if __name__ == "__main__":
    TestResizeImage()
