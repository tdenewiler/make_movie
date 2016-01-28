Make Movie
==========
This repository contains a Python script that will take all images in a directory and make a time-lapse movie. EXIF data is utilized to determine the date the picture was taken and that date is printed on each of the images in the movie.

The maximum width and height, frame rate, temporary image directory, and output filename are all configurable from the command line. If a music file is specified for background audio then the track length will be used to determine the required frame rate to fill the song.

A separate script to test resizing images is also included.
