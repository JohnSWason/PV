#!/usr/bin/python

# --------------------------------------------------------------------------
# DotStar Light Painter for Raspberry Pi.
#
# Hardware requirements:
# - Raspberry Pi computer (any model)
# - DotStar LED strip (any length, but 144 pixel/m is ideal)
# - One 74AHCT125 logic level shifter IC
# - High-current, high-capacity USB battery bank such as
#
# Software requirements:
# - Raspbian (2015-05-05 "Wheezy" version recommended; can work with Jessie
#   or other versions, but Wheezy's a bit smaller and boots to the command
#   line by default).
# - Adafruit DotStar library for Raspberry Pi:
#   github.com/adafruit/Adafruit_DotStar_Pi
# - usbmount:
#   sudo apt-get install usbmount
#   See file "99_lightpaint_mount" for add'l info.
#
# Written by Phil Burgess / Paint Your Dragon for Adafruit Industries.
# Heavily modified by John Watson for Dr Tamara Watson
#
# Adafruit invests time and resources providing this open source code,
# please support Adafruit and open-source hardware by purchasing products
# from Adafruit!
# --------------------------------------------------------------------------

import os
import select
import signal
import time
import RPi.GPIO as GPIO
import pv_menu
import pv_log
from dotstar import Adafruit_DotStar
from evdev import InputDevice, ecodes
from lightpaint import LightPaint
from PIL import Image

# CONFIGURABLE STUFF -------------------------------------------------------

num_leds   = 144    # Length of LED strip, in pixels
order      = 'brg'  # 'brg' for current DotStars, 'gbr' for pre-2015 strips
vflip      = 'true' # 'true' if strip input at bottom, else 'false'

# DotStar strip data & clock MUST connect to hardware SPI pins
# (GPIO 10 & 11).  12000000 (12 MHz) is the SPI clock rate; this is the
# fastest I could reliably operate a 288-pixel strip without glitching.
# You can try faster, or may need to set it lower, no telling.
# If using older (pre-2015) DotStar strips, declare "order='gbr'" above
# for correct color order.
strip = Adafruit_DotStar(num_leds, 12000000, order=order)

path      = '/media/usb'             # USB stick mount point
logfile   = '/media/usb/pv_log.txt'    # USB stick mount point
mousefile = '/dev/input/mouse0'      # Mouse device (as positional encoder)
eventfile = '/dev/input/event0'      # Mouse events accumulate here
dev       = None                     # None unless mouse is detected
Experimentdesignation = 'No designation'
Subjectname = 'No subject'
RateMode = 'Not set'

gamma          = (2.8, 2.8, 2.8) # Gamma correction curves for R,G,B
color_balance  = (128, 255, 180) # Max brightness for R,G,B (white balance)
power_settings = (1450, 1550)    # Battery avg and peak current

# INITIALIZATION -----------------------------------------------------------

strip.begin() # Initialize SPI pins for output

ledBuf     = strip.getPixels() # Pointer to 'raw' LED strip data
clearBuf   = bytearray([0xFF, 0, 0, 0] * num_leds)
imgNum     = 0    # Index of currently-active image
imgwidth   = 0.0  # Image width in pixels
duration   = 2.0  # Image paint time, in seconds
filename   = None # List of image files (nothing loaded yet)
lightpaint = None # LightPaint object for currently-active image (none yet)


# FUNCTIONS ----------------------------------------------------------------

# Signal handler when SIGUSR1 is received (USB flash drive mounted,
# triggered by usbmount and 99_lightpaint_mount script).
def sigusr1_handler(signum, frame):
    scandir()
    pv_menu.pv_menu_initialise(filename)

# Ditto for SIGUSR2 (USB drive removed -- clears image file list)
def sigusr2_handler(signum, frame):
    global filename
    filename = None
    imgNum   = 0
    pv_menu.pv_menu_initialise(filename)
    # Current LightPaint object is left resident

# Scan root folder of USB drive for viable image files.
def scandir():
    global imgNum, lightpaint, filename
    
    files     = os.listdir(path)
    num_files = len(files) # Total # of files, whether images or not
    filename  = []         # Filename list of valid images
    imgNum    = 0
    if num_files == 0:
        #    print '\tNo files found'
        return
    for i, f in enumerate(files):
        lower =  i      * num_leds / num_files
        upper = (i + 1) * num_leds / num_files
        for n in range(lower, upper):
            strip.setPixelColor(n, 0x010100) # Yellow

        if f[0] == '.': continue
        try:    Image.open(os.path.join(path, f))
        except: continue   # Is directory or non-image file; skip
        filename.append(f) # Valid image, add to list


    if len(filename) > 0:                  # Found some image files?
        filename.sort()                # Sort list alphabetically
        lightpaint = loadImage(imgNum) # Load first image

# Load image, do some conversion and processing as needed before painting.
def loadImage(index):
    global imgwidth

    num_images = len(filename)
    lower      =  index      * num_leds / num_images
    upper      = (index + 1) * num_leds / num_images
    for n in range(lower, upper):
        strip.setPixelColor(n, 0x010000) # Red = loading

    startTime = time.time()
    # Load image, convert to RGB if needed
    img = Image.open(os.path.join(path, filename[index])).convert("RGB")
    imgwidth = img.size[0]

    # If necessary, image is vertically scaled to match LED strip.
    # Width is NOT resized, this is on purpose.  Pixels need not be
    # square!  This makes for higher-resolution painting on the X axis.
    if img.size[1] != num_leds:
        img = img.resize((img.size[0], num_leds), Image.BICUBIC)

    # Convert raw RGB pixel data to a string buffer.
    # The C module can easily work with this format.
    pixels = img.tostring()
    #print "\t%f seconds" % (time.time() - startTime)

    # Do external C processing on image; this provides 16-bit gamma
    # correction, diffusion dithering and brightness adjustment to
    # match power source capabilities.
    for n in range(lower, upper):
        strip.setPixelColor(n, 0x010100) # Yellow

    startTime  = time.time()
    # Pixel buffer, image size, gamma, color balance and power settings
    # are REQUIRED arguments.  One or two additional arguments may
    # optionally be specified:  "order='gbr'" changes the DotStar LED
    # color component order to be compatible with older strips (same
    # setting needs to be present in the Adafruit_DotStar declaration
    # near the top of this code).  "vflip='true'" indicates that the
    # input end of the strip is at the bottom, rather than top (I
    # prefer having the Pi at the bottom as it provides some weight).
    # Returns a LightPaint object which is used later for dithering
    # and display.
    lightpaint = LightPaint(pixels, img.size, gamma, color_balance,
      power_settings, order=order, vflip=vflip)
    #print "\t%f seconds" % (time.time() - startTime)

    # Success!
    for n in range(lower, upper):
        strip.setPixelColor(n, 0x000100) # Green
#    strip.show()
    time.sleep(0.25) # Tiny delay so green 'ready' is visible
    #print "Ready!"

    strip.clear()
    strip.show()
    return lightpaint


# MAIN LOOP ----------------------------------------------------------------
    
os.system('clear')                        # clear the terminal screen
Experimentdesignation  = raw_input("\n\n\tExperiment designation: ")


# Init some stuff for speed selection...
max_time    = 10.0
min_time    =  0.1
time_range  = (max_time - min_time)
speed_pixel = int(num_leds * (duration - min_time) / time_range)
duration    = min_time + time_range * speed_pixel / (num_leds - 1)
prev_btn    = 0
rep_time    = 0.2
nowpainting = 0          # Index of current image loaded, starts with the first one

scandir() # USB drive might already be inserted
signal.signal(signal.SIGUSR1, sigusr1_handler) # USB mount signal
signal.signal(signal.SIGUSR2, sigusr2_handler) # USB unmount signal

# Being in every way ready to see, proceed to show
pv_menu.pv_menu_initialise(500,filename,Experimentdesignation)
pv_log.logstart(logfile,Experimentdesignation)
pv_log.logfiles(len(filename),filename)
stripes = [float(0)]

# Try and loop on the menu inputs
# Loop ends when Quit or Shutdown is selected
try:
    while True:
        # show the menu and get selections
        delay, speed, imagetopaint, Experimentdesignation, Subjectname, RateMode = pv_menu.pv_menu_show()
       
        if nowpainting <> imagetopaint:
            lightpaint = loadImage(imagetopaint)
            nowpainting = imagetopaint

        print 'Ready to print', filename[imagetopaint]
        pv_log.logpaint(delay, speed, filename[imagetopaint], Experimentdesignation, Subjectname, RateMode)

        stripes = [None] * imgwidth
        for n in range(0, imgwidth):
            stripes[n] = n / float(imgwidth)

        choice = raw_input("Ready press Enter to continue: ") 
        
        # Paint!
        if RateMode == 'Whole image':
            startTime = time.time()
            while True:
                #Whole image
                duration =time_range*(1-(speed/1000))+min_time
                t1        = time.time()
                elapsed   = t1 - startTime
                if elapsed > duration: break
                # dither() function is passed a
                # destination buffer and a float
                # from 0.0 to 1.0 indicating which
                # column of the source image to
                # render.  Interpolation happens.
                lightpaint.dither(ledBuf,elapsed / duration)
                strip.show(ledBuf)
#                print 'elp,  dur, e/d',elapsed, duration, elapsed / duration
        elif RateMode == 'Slice by slice':
            for n in range(0, imgwidth):
                lightpaint.dither(ledBuf,stripes[n])
                strip.show(ledBuf)
                time.sleep(delay)
        else:
            print 'Invalid rate mode'
        
        strip.show(clearBuf)
        pv_log.logresult(raw_input("Result: ") )
        

except KeyboardInterrupt:
    print "Cleaning up"
    strip.clear()
    strip.show()
    print "Done!"
