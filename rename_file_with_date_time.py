#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
In a directory containing images rename the files to use
the format of IMG_<YYYYMMDD>_<HHMMSSSS>.<ext>.
Get the date and time from image metadata.
Tested specifically with HTC One (M8) that uses numbers
instead of date in filenames.
'''

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
from shutil import copyfile

class RenameFileWithDateTime():
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-s", "--source_dir", dest="source_directory", help="Directory containing original images. Default to current directory.", default='.')
        parser.add_option("-t", "--tmp_dir", dest="tmp_directory", help="Directory containing temporary images. Default to tmp.", default='tmp')
        options, args = parser.parse_args(sys.argv)
        source_dir = options.source_directory
        new_image_directory = options.tmp_directory
        num_files = len(os.walk(source_dir).next()[2])

        if num_files > 0:
            self.create_files(source_dir, new_image_directory)
        else:
            print 'No files in %s' % (source_dir)

    def create_files(self, source_dir, tmp_dir):
        valid_extensions = ['png', 'jpg']
        image_names = {}
        for path, dirs, files in os.walk(source_dir):
            for filename in files:
                ext = filename[-3:].lower()
                if ext not in valid_extensions:
                    continue

                print 'Opening %s' % (filename)
                if os.path.isfile(source_dir + filename):
                    current_image = Image.open(source_dir+filename)
                    info = current_image._getexif()
                    if 36867 in info:
                        if info[272] == 'HTC6525LVW':
                            print 'info[36867] =', info[36867]
                            new_filename = str(info[36867]).replace(':', '').upper()
                            new_filename = new_filename.replace(' ', '_')
                        else:
                            new_filename = str(info[36867]).replace(':', '')[:-7].upper()
                    else:
                        new_filename = str(info[306]).replace(':', '')[:-7].upper()
                    new_filename = tmp_dir + '/' + 'IMG_' + new_filename + '.jpg'
                    print 'Original filename = %s, new filename = %s' % (filename, new_filename)
                    try:
                        copyfile(source_dir+'/'+filename, new_filename)
                    except:
                        print 'Exception caught renaming %s --> %s' % (filename, new_filename)
                else:
                    print '%s is not a file, skipping' % (filename)
                print '*****'

if __name__ == '__main__':
    RenameFileWithDateTime()
