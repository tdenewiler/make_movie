#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
In a directory containing images create a time-lapse movie.
Requires adding border to make all images the same resolution.
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

class MakeMovie():
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-s", "--source_dir", dest="source_directory", help="Directory containing original images. Default to current directory.", default='.')
        parser.add_option("-t", "--tmp_dir", dest="tmp_directory", help="Directory containing temporary images. Default to tmp.", default='tmp')
        parser.add_option("-f", "--frame_rate", dest="fps", help="Frames per second for the output movie. Default to 2.", default=2)
        parser.add_option("-o", "--output_filename", dest="output_filename", help="Output filename. Default to movie.", default='movie')
        parser.add_option("-w", "--max_width", dest="max_width", help="Maximum width of output video. Default to 1920.", default=1920)
        parser.add_option("-e", "--max_height", dest="max_height", help="Maximum height of output video. Default to 1280.", default=1280)
        options, args = parser.parse_args(sys.argv)
        source_dir = options.source_directory
        new_image_directory = options.tmp_directory
        absolute_max_width = options.max_width
        absolute_max_height = options.max_height

        image_names = self.get_image_names(source_dir)
        max_width, max_height = self.get_max_image_resolution(image_names, absolute_max_width, absolute_max_height)
        print 'Found %d images and setting resolution to (w, h) = (%d, %d).' % (len(image_names), max_width, max_height)
        self.add_border_to_images(image_names, source_dir, new_image_directory, max_width, max_height)
        self.make_movie(new_image_directory, max_width, max_height, options.fps, options.output_filename)

    def add_border_to_images(self, image_list, source_directory, new_image_directory, max_width, max_height):
        for timestamp, image in image_list.iteritems():
            new_size = (max_width, max_height)
            new_image = Image.new("RGB", new_size)
            orig_image = Image.open(image)
            orig_size = orig_image.size
            scale_ratio = 1.0
            if orig_size[0] > max_width or orig_size[1] > max_height:
                w_ratio = max_width / orig_size[0]
                h_ratio = max_height / orig_size[1]
                scale_ratio = min(w_ratio, h_ratio)
                orig_image = orig_image.resize(((int(orig_size[0] * scale_ratio)), int(orig_size[1] * scale_ratio)), Image.ANTIALIAS)
            new_image.paste(orig_image, (int((new_size[0] - orig_size[0] * scale_ratio) / 2), int((new_size[1] - orig_size[1] * scale_ratio) / 2)))
            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 120)
            in_date = datetime.strptime(timestamp, '%Y%m%d')
            out_date = in_date.strftime('%B %d, %Y')
            draw.text((100, 1100), out_date, (255,255,255), font=font)
            new_name = image[len(source_directory):]
            new_name = new_image_directory+'/'+new_name
            new_image.save(new_name)

    def get_max_image_resolution(self, image_list, absolute_max_width, absolute_max_height):
        max_height = 0
        max_width = 0
        for timestamp, image in image_list.iteritems():
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

        return max_width, max_height

    def get_image_names(self, source_dir):
        valid_extensions = ['png', 'jpg']
        image_names = {}
        for path, dirs, files in os.walk(source_dir):
            for filename in files:
                ext = filename[-3:].lower()
                if ext not in valid_extensions:
                    continue

                current_image = Image.open(source_dir+filename)
                info = current_image._getexif()
                if 36867 in info:
                    timestamp = str(info[36867]).replace(':', '')[:-7].upper()
                else:
                    timestamp = str(info[306]).replace(':', '')[:-7].upper()
                image_names[timestamp] = source_dir+filename

        image_names_sorted = collections.OrderedDict(sorted(image_names.items(), key=itemgetter(0)))
        return image_names_sorted

    def make_movie(self, image_dir, width, height, fps, output_filename):
        command = ('mencoder',
            'mf://'+image_dir+'/*.jpg',
            '-mf',
            'type=jpg:w='+str(width)+':h='+str(height)+':fps='+str(fps),
            '-ovc',
            'x264',
            '-x264encopts',
            'bitrate=1200:threads=2',
            '-of',
            'rawvideo',
            '-o',
            output_filename)

        print "\nabout to execute:\n%s\n" % ' '.join(command)
        subprocess.check_call(command)

if __name__ == '__main__':
    make_movie = MakeMovie()
