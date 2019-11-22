# Make Movie

| Service | Status |
| ------- | ------ |
| Build   | [![Travis-CI](https://api.travis-ci.org/tdenewiler/make_movie.svg?branch=master)](https://travis-ci.org/tdenewiler/make_movie/branches) |

This repository contains a Python script that will take all images in a directory and make a time-lapse movie.
EXIF data is utilized to determine the date the picture was taken and that date is printed on each of the images in
the movie.

The maximum width and height, frame rate, temporary image directory, and output filename are all configurable from
the command line.
If a music file is specified for background audio then the track length will be used to determine the required frame
rate to fill the song.

## Dependencies

To install dependencies use the following:

```shell
sudo -H pip install -r requirements.txt
cat install.txt | xargs sudo apt install
```

## Music

To combine multiple music files into a single file a solution was presented at
<https://askubuntu.com/questions/20507/concatenating-several-mp3-files-into-one-mp3>.
That is why the `mp3wrap` package is listed in the apt dependencies in `install.txt`.

```shell
mp3wrap output.mp3 input-1.mp3 input-2.mp3 input-3.mp3
```

