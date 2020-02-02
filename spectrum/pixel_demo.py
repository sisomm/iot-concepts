# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
 
import time
import neopixel 
import argparse
import board
 
# LED strip configuration:
PIXELS      = 50      # Number of LED pixels.
 
 
 
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(len(strip)):
        strip[i]=color
        time.sleep(wait_ms/1000.0)
 
def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, len(strip)-2, 3):
                strip[i+q]=color
            time.sleep(wait_ms/1000.0)
            for i in range(0, len(strip)-2, 3):
                strip[i+q]=0
 
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)
 
def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(len(strip)):
            strip[i]= wheel((i+j) & 255)
        #time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(len(strip)):
            strip[i]= wheel((int(i * 256 / len(strip)) + j) & 255)
        #time.sleep(wait_ms/1000.0)
 
def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, len(strip), 3):
                strip[i+q]= wheel((i+j) % 255)
            time.sleep(wait_ms/1000.0)
            for i in range(0, len(strip), 3):
                strip[i+q]= 0
 
# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
 
    # Create NeoPixel object with appropriate configuration.
    strip = neopixel.NeoPixel(board.D18, PIXELS,bpp=3,pixel_order=neopixel.RGB)
 
    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
 
    try:
 
        while True:
            print ('Color wipe animations.')
            colorWipe(strip, (255, 0, 0))  # Red wipe
            colorWipe(strip, (0, 255, 0))  # Blue wipe
            colorWipe(strip, (0, 0, 255))  # Green wipe
            print ('Theater chase animations.')
            strip.fill(0)
            theaterChase(strip, (127, 127, 127))  # White theater chase
            theaterChase(strip, (127,   0,   0))  # Red theater chase
            theaterChase(strip, (  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)
 
    except KeyboardInterrupt:
        if args.clear:
            strip.fill(0)
 
