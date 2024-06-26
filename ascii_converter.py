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

size = None

# Help Formatter
def formatter(prog): return argparse.HelpFormatter(prog, max_help_position=50, width=100)

# Parse arguments
parser = argparse.ArgumentParser(description='A program to convert images to ascii-art', formatter_class=formatter)
parser.add_argument('file', help='image file to be converted')
parser.add_argument('-s', '--size', type=int, metavar='int', help='change size of ascii output')
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

def get_new_size(img):
  global size
  
  if args.size:
    return args.size
  
  else:
    old_size = size
    
    term_w, term_h = tuple(os.get_terminal_size())
    img_w, img_h = img.size

    term_w /= 2

    if img_w / term_w > img_h / term_h:
      size = term_w * max(img_h / img_w, 1) * 2 - 1
    else:
      size = term_h * max(img_w / img_h, 1) * 2 - 1

    if size != old_size:
      os.system('cls')
  
    return size

# Reformat image
def reformat_img(img):
  # Resize
  new_size = get_new_size(img)
  img.thumbnail((new_size, new_size), Image.Resampling.NEAREST if args.nearest else None)

  # Enhance image
  if args.invert: img = ImageOps.invert(img)
  img = ImageEnhance.Brightness(img).enhance(args.brightness)
  img = ImageEnhance.Contrast(img).enhance(args.contrast)
  
  img = img.convert('RGB')  # Remove alpha channel
  
  if not args.color:
    # Dither
    if args.dither:
      img = img.quantize(colors=len(CHARS), palette=img.quantize(len(CHARS)))

    # Convert to grayscale
    img = img.convert('L')

  return img


# Print ascii characters based on pixel value
def print_ascii(img):
  px_value = img.load()

  for y in range(img.height // 2):
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
        i = math.floor(px_value[x, y * 2] / (256 / len(CHARS)))
        print(CHARS[i], end='')
    print()  # New line


def main():
  ext = args.file.split('.')[-1]

  if ext == 'gif':
    img = Image.open(args.file)

    # Hide cursor
    print('\033[?25l', end="")

    # Bug: gif stops at second to last frame if looping is turned off
    try:
      while args.loop or img.tell() < img.n_frames - 1:
        start_time = time.perf_counter()

        cur_frame = img.copy()
        cur_frame = reformat_img(cur_frame)
        
        # Reset cursor position
        print('\033[0;0H', end='')

        print_ascii(cur_frame)

        # Seek next frame
        img.seek((img.tell() + 1) % img.n_frames)
        
        end_time = time.perf_counter() - start_time
        time.sleep(max(img.info['duration'] / 1000 - end_time, 0))
    except KeyboardInterrupt:
      os.system('cls')
      print('\033[?25h', end="")  # Show cursor

  elif ext in ('mp4', 'webm', 'flv'):
    video = cv2.VideoCapture(args.file)
    fps = video.get(cv2.CAP_PROP_FPS)

    # Hide cursor
    print('\033[?25l', end="")

    try:
      while True:
        start_time = time.perf_counter()

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
        cur_frame = reformat_img(cur_frame)

        # Reset cursor position
        print('\033[0;0H', end='')
        
        print_ascii(cur_frame)

        end_time = time.perf_counter() - start_time
        time.sleep(max(1 / fps - end_time, 0))
    except KeyboardInterrupt:
      video.release()
      os.system('cls')
      print('\033[?25h', end="")  # Show cursor

  elif ext in ('png', 'jpg'):
    img = Image.open(args.file)
    img = reformat_img(img)
    print_ascii(img)


if __name__ == '__main__':
  main()
