#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
In a directory containing images create a time-lapse movie.
Requires adding border to make all images the same resolution.
'''

from __future__ import division
from PIL import Image, ImageFont, ImageDraw
from optparse import OptionParser
import os
import sys
import subprocess
from datetime import datetime
from operator import itemgetter
import collections
from mutagen.mp3 import MP3

class MakeMovie(object):
    '''
    Make a movie using image files.
    '''
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-s", "--source_dir", dest="source_directory",
            help="Directory containing original images. \
            Default to current directory.", default='.')
        parser.add_option("-t", "--tmp_dir", dest="tmp_directory",
            help="Directory containing temporary images. Default to tmp.",
            default='tmp')
        parser.add_option("-f", "--frame_rate", dest="fps",
            help="Frames per second for the output movie. Default to 2.",
            default=2)
        parser.add_option("-o", "--output_filename", dest="output_filename",
            help="Output filename. Default to movie.", default='movie')
        parser.add_option("-w", "--max_width", dest="max_width",
            help="Maximum width of output video. Default to 1920.",
            default=1920)
        parser.add_option("-e", "--max_height", dest="max_height",
            help="Maximum height of output video. Default to 1280.",
            default=1280)
        parser.add_option("-m", "--music", dest="music",
            help="Name of audio file to add to video.",
            default='')
        options, dummy = parser.parse_args(sys.argv)
        source_dir = options.source_directory
        new_image_directory = options.tmp_directory
        absolute_max_width = options.max_width
        absolute_max_height = options.max_height
        fps = options.fps

        image_names = self.get_image_names(source_dir)
        size = self.get_max_image_resolution(image_names,
            absolute_max_width, absolute_max_height)
        print 'Found %d images and setting resolution to (w, h) = (%d, %d).' % \
            (len(image_names), size[0], size[1])
        self.add_border_to_images(image_names, source_dir, new_image_directory,
            size)
        if options.music != '':
            print 'Adding soundtrack: {}'.format(options.music)
            audio = MP3(options.music)
            print 'song length = {}s'.format(audio.info.length)
            fps = len(image_names) / audio.info.length
            print 'fps = {}'.format(fps)

        self.make_movie(new_image_directory, size, fps, options.music,
            options.output_filename)
        if options.music != '':
            self.add_music(options.output_filename, options.music)

    @classmethod
    # pylint: disable=too-many-locals
    def add_border_to_images(cls, image_list, source_directory,
        new_image_directory, size):
    # pylint: enable=too-many-locals
        '''
        Add border to images to make them all the same size.
        '''
        img_num = 1
        for timestamp, image in image_list.iteritems():
            new_image = Image.new("RGB", size)
            orig_image = Image.open(image)
            orig_size = orig_image.size
            scale_ratio = 1.0
            if orig_size[0] > size[0] or orig_size[1] > size[1]:
                scale_ratio = min(size[0] / orig_size[0],
                    size[1] / orig_size[1])
                orig_image = orig_image.resize(((int(orig_size[0] *
                    scale_ratio)), int(orig_size[1] * scale_ratio)),
                    Image.ANTIALIAS)
            new_image.paste(orig_image, (int((size[0] - orig_size[0] *
                scale_ratio) / 2), int((size[1] - orig_size[1] *
                scale_ratio) / 2)))
            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype \
                ("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 120)
            date = datetime.strptime(timestamp, '%Y%m%d')
            date = date.strftime('%B %d, %Y')
            draw.text((100, 1100), date, (255, 255, 255), font=font)
            new_name = image[len(source_directory):]
            new_name = new_image_directory + '/image_' + str(img_num).zfill(5) \
                + '.jpg'
            new_image.save(new_name)
            img_num += 1

    @classmethod
    def get_max_image_resolution(cls, image_list, absolute_max_width,
        absolute_max_height):
        '''
        From a list of images find the maximum height and width.
        '''
        max_height = 0
        max_width = 0
        for dummy, image in image_list.iteritems():
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
        '''
        Get the filenames of images in a directory.
        '''
        valid_extensions = ['png', 'jpg']
        image_names = {}
        for dummy, dummy, files in os.walk(source_dir):
            for filename in files:
                ext = filename[-3:].lower()
                if ext not in valid_extensions:
                    continue

                current_image = Image.open(source_dir+filename)
                # pylint: disable=protected-access
                info = current_image._getexif()
                # pylint: enable=protected-access
                if 36867 in info:
                    timestamp = str(info[36867]).replace(':', '')[:-7].upper()
                elif 36868 in info:
                    timestamp = str(info[36868]).replace(':', '')[:-7].upper()
                else:
                    timestamp = str(info[306]).replace(':', '')[:-7].upper()
                image_names[timestamp] = source_dir+filename

        image_names_sorted = collections.OrderedDict(sorted(image_names.items(),
            key=itemgetter(0)))
        return image_names_sorted

    @classmethod
    # pylint: disable=too-many-arguments
    def make_movie(cls, image_dir, size, fps, music, output_filename):
    # pylint: enable=too-many-arguments
        '''
        Create a movie using images in a specified directory.
        '''
        command = ('mencoder',
            'mf://'+image_dir+'/*.jpg',
            '-mf',
            'type=jpg:w='+str(size[0])+':h='+str(size[1])+':fps='+str(fps),
            '-ovc',
            'x264',
            '-x264encopts',
            'bitrate=1200:threads=2',
            '-of',
            'rawvideo',
            '-audiofile',
            music,
            '-oac',
            'copy',
            '-o',
            output_filename)

        command = ('avconv',
            '-r',
            str(fps),
            '-i',
            'tmp/image_%05d.jpg',
            '-b:v',
            '1000k',
            output_filename)

        print "\nabout to execute:\n%s\n" % ' '.join(command)
        subprocess.check_call(command)

    @classmethod
    def add_music(cls, output_filename, music):
        """
        Add a song as background music for video.
        """
        command = ('avconv',
            '-i',
            output_filename,
            '-i',
            music,
            '-map',
            '0:0',
            '-map',
            '1:0',
            '-vcodec',
            'copy',
            '-acodec',
            'copy',
            'music-' + output_filename)

        print "\nabout to execute:\n%s\n" % ' '.join(command)
        subprocess.check_call(command)

if __name__ == '__main__':
    MakeMovie()
