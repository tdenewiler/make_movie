#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
In a directory containing images create a time-lapse movie.
Requires adding border to make all images the same resolution.
'''

from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS
from pprint import pprint
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
        parser.add_option("-o", "--output_filename", dest="output_filename", help="Output filename. Default to movie.", default='movie')
        options, args = parser.parse_args(sys.argv)
        source_dir = options.source_directory
        new_image_directory = options.tmp_directory

        image_names = self.get_image_names(source_dir)
        max_height, max_width = self.get_max_image_resolution(image_names)
        self.add_border_to_images(image_names, max_height, max_width, source_dir, new_image_directory)
        self.make_movie(new_image_directory, max_width, max_height, options.output_filename)

    def add_border_to_images(self, image_list, new_height, new_width, source_directory, new_image_directory):
        new_size = (new_height, new_width)
        for timestamp, image in image_list.iteritems():
            new_image = Image.new("RGB", new_size)
            orig_image = Image.open(image)
            orig_size = orig_image.size
            new_image.paste(orig_image, ((new_size[0] - orig_size[0]) / 2, (new_size[1] - orig_size[1]) / 2))
            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 160)
            in_date = datetime.strptime(timestamp, '%Y%m%d')
            out_date = in_date.strftime('%B %d, %Y')
            draw.text((100, 3000), out_date, (255,255,255), font=font)
            new_name = image[len(source_directory):]
            new_name = new_image_directory+'/'+new_name
            new_image.save(new_name)

    def get_max_image_resolution(self, image_list):
        max_height = 0
        max_width = 0
        for timestamp, image in image_list.iteritems():
            orig_image = Image.open(image)
            orig_size = orig_image.size
            if orig_size[1] > max_height:
                max_height = orig_size[1]
            if orig_size[0] > max_width:
                max_width = orig_size[0]

        return max_height, max_width

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

    def make_movie(self, image_dir, width, height, output_filename):
        command = ('mencoder',
            'mf://'+image_dir+'/*',
            '-mf',
            'type=jpg:w='+str(width)+':h='+str(height)+':fps=2',
            '-ovc',
            'lavc',
            '-lavcopts',
            'vcodec=mpeg4',
            '-oac',
            'copy',
            '-o',
            output_filename)

        print "\nabout to execute:\n%s\n" % ' '.join(command)
        subprocess.check_call(command)

if __name__ == '__main__':
    make_movie = MakeMovie()
