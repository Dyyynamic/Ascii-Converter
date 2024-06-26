# Ascii Converter in Python

Image, GIF and Video to ascii converter made using python

Inspiration was taken from the following articles:

- http://paulbourke.net/dataformats/asciiart/
- https://jod.li/2020/11/14/optimal-character-choices-for-ascii-art-in-php/

## Running

Install OpenCV and Pillow using PIP:

```
pip install opencv-python pillow
```

Run using Python 3:

```
python3 ascii_converter.py your_image.jpg
```

## TODO

- [x] Add GIF support
- [x] Combine all versions into a single program
- [x] Add video support
- [x] Implement dithering
- [x] Implement a proper way to exit in the middle of a GIF/video
- [ ] Optimize color output
- [ ] Clean up and implement hue.py into the main program
  - Separate 'color' parameter into color and chars/blocks
  - Consider using HSV instead of RGB
