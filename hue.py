import argparse, math, os, time, cv2
from PIL import Image, ImageEnhance, ImageOps, GifImagePlugin

# Set image mode of first frame to RGB instead of P
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS

CHARSETS = {
  'default':  ' .:-"+1a#@',
  'block': ' ░▒▓█',
  'quadrants': ' ▖▞▟██',
  'horizontal': ' ▁▂▃▄▅▆▇█',
  'vertical': ' ▏▎▍▌▋▊▉█',
  'braille': ' ⠠⢂⡑⡪⡮⡾⣾⣿',
  'braille2': ' ⠠⢂⡑⡪⡮⡾⣾⣿1A#@'
}

RESET = '\033[0m'

# Help Formatter
def formatter(prog): return argparse.HelpFormatter(prog, max_help_position=50, width=100)

# Parse arguments
parser = argparse.ArgumentParser(description='A program to convert images to ascii-art', formatter_class=formatter)
parser.add_argument('file', help='image file to be converted')
parser.add_argument('-s', '--size', type=int, default=100, metavar='int', help='change size of ascii output')
parser.add_argument('-b', '--brightness', type=float, default=1.0, metavar='float',
                    help='change brightness of ascii output')
parser.add_argument('-c', '--contrast', type=float, default=1.0, metavar='float',
                    help='change contrast of ascii output')
parser.add_argument('-cs', '--charset', type=str, default='default', metavar='str',
                    help=f'change ascii charset, available choices are: {", ".join(CHARSETS)}.')
parser.add_argument('-i', '--invert', action='store_true', help='invert ascii output')
parser.add_argument('-col', '--color', action='store_true', help='draw color instead of ascii')
parser.add_argument('-l', '--loop', action='store_true', help='loop gif or video')
parser.add_argument('-n', '--nearest', action='store_true', help='when scaling, use nearest neighbor resampling')
parser.add_argument('-d', '--dither', action='store_true', help='dither ascii output, not recommended for GIFs/videos')
args = parser.parse_args()

CHARS = CHARSETS[args.charset]

# Reformat image
def reformat_img(img):
  # Resize
  img.thumbnail((args.size, args.size), Image.Resampling.NEAREST if args.nearest else None)

  # Enhance image
  if args.invert: img = ImageOps.invert(img)
  img = ImageEnhance.Brightness(img).enhance(args.brightness)
  img = ImageEnhance.Contrast(img).enhance(args.contrast)
  
  img = img.convert('RGB')  # Remove alpha channel
  
  if not args.color:
    # Dither
    if args.dither:
      img2 = img.quantize(colors=len(CHARS), palette=img.quantize(len(CHARS)))

    # Convert to grayscale
    img2 = img.convert('L')

  return (img2, img)


# Print ascii characters based on pixel value
def print_ascii(img, img2):
  px_value = img.load()
  px_value2 = img2.load()

  for y in range(math.floor(img.height / 2)):
    for x in range(img.width):
      if args.color:
        # Background, top half
        r, g, b = px_value[x, y * 2]
        bg = f'\033[48;2;{r};{g};{b}m'

        # Foreground, bottom half
        r, g, b = px_value[x, y * 2 + 1]
        fg = f'\033[38;2;{r};{g};{b}m'

        print(bg + fg + '▄' + RESET, end='')
      else:
        # Foreground, bottom half
        r, g, b = px_value2[x, y * 2 + 1]
        fg = f'\033[38;2;{r};{g};{b}m'

        i = math.floor(px_value[x, y * 2] / (256 / len(CHARS)))
        print(fg + CHARS[i], end='')
    print()  # New line


def main():
  ext = args.file.split('.')[-1]

  if ext == 'gif':
    img = Image.open(args.file)
    os.system('cls')

    # Hide cursor
    print('\033[?25l', end="")

    # Bug: gif stops at second to last frame if looping is turned off
    while args.loop or img.tell() < img.n_frames - 1:
      start_time = time.time()

      cur_frame = img.copy()
      cur_frame, cur_frame2 = reformat_img(cur_frame)
      
      # Reset cursor position
      print('\033[0;0H', end='')

      print_ascii(cur_frame, cur_frame2)

      # Seek next frame
      img.seek((img.tell() + 1) % img.n_frames)
      
      end_time = time.time() - start_time
      time.sleep(max(img.info['duration'] / 1000 - end_time, 0))
    
    # Show cursor
    print('\033[?25h', end="")

  elif ext in ('mp4', 'webm', 'flv'):
    video = cv2.VideoCapture(args.file)
    fps = video.get(cv2.CAP_PROP_FPS)
    os.system('cls')

    # Hide cursor
    print('\033[?25l', end="")

    while True:
      start_time = time.time()

      success, cur_frame = video.read()

      # End of video
      if not success:
        if args.loop:
          video.set(cv2.CAP_PROP_POS_FRAMES, 0)
          continue
        else:
          break

      cur_frame = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
      cur_frame = Image.fromarray(cur_frame)  # Convert to PIL image
      cur_frame, cur_frame2 = reformat_img(cur_frame)

      # Reset cursor position
      print('\033[0;0H', end='')
      
      print_ascii(cur_frame, cur_frame2)

      end_time = time.time() - start_time
      time.sleep(max(1 / fps - end_time, 0))
    
    # Show cursor
    print('\033[?25h', end="")
    video.release()

  elif ext in ('png', 'jpg'):
    img = Image.open(args.file)
    img, img2 = reformat_img(img)
    print_ascii(img, img2)


if __name__ == '__main__':
  main()
