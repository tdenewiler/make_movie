#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Resize an image.
'''

from __future__ import division
from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS
from optparse import OptionParser
import os
import sys
import subprocess
from datetime import datetime
from time import strptime
from operator import itemgetter
import collections

class TestResizeImage():
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-i", "--input_filename", dest="input_filename", help="Input filename. Default to empty.", default='')
        parser.add_option("-o", "--output_filename", dest="output_filename", help="Output filename. Default to movie.", default='movie')
        options, args = parser.parse_args(sys.argv)
        image_max_width = 1920
        image_max_height = 1280

        self.resize_image(options.input_filename, options.output_filename, image_max_width, image_max_height)

    def resize_image(self, input_filename, output_filename, max_width, max_height):
        print 'Resizing %s' % input_filename
        orig_image = Image.open(input_filename)
        orig_size = orig_image.size
        new_size = (max_width, max_height)
        new_image = Image.new("RGB", new_size)
        if orig_size[0] > max_width or orig_size[1] > max_height:
            print 'Original size is (%d, %d) and max size is (%d, %d)' % (orig_size[0], orig_size[1], max_width, max_height)
            w_ratio = max_width / orig_size[0]
            h_ratio = max_height / orig_size[1]
            scale_ratio = min(w_ratio, h_ratio)
            print 'Resized %s using ratio of %.2f since w_ratio = %.2f and h_ratio = %.2f' % (input_filename, scale_ratio, w_ratio, h_ratio)
            orig_image = orig_image.resize(((int(orig_size[0] * scale_ratio)), int(orig_size[1] * scale_ratio)), Image.ANTIALIAS)
            print 'orig_image is now (%d, %d)' % ((int(orig_size[0] * scale_ratio)), int(orig_size[1] * scale_ratio))
        new_image.paste(orig_image, (int((new_size[0] - orig_size[0] * scale_ratio) / 2), int((new_size[1] - orig_size[1] * scale_ratio) / 2)))
        new_image.save(output_filename)

if __name__ == '__main__':
    tri = TestResizeImage()
