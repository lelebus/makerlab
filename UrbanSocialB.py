#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from neopixel import *
import argparse
import vlc
import web
web.url = "http://requestbin.net/r/1j4k3wp1" 

GPIO.setmode(GPIO.BCM)

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.

# LED_PIN1        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN2        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).

LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

GPIO_TRIGGER    = 10    #PIN SENSOR 1
GPIO_ECHO       = 24    #ECHO SENSOR 1
LED_PIN1        = 20    #PIN LED 1      AGGIUNTO
GPIO_TRIGGER1   = 8     #PIN SENSOR 2
GPIO_ECHO1      = 25    #ECHO SENSOR 2
LED_PIN2        = 21    #PIN LED 2      AGGIUNTO

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)


def animation(strip, color, wait_ms=30):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def distance(Trigger, echo, i):
    GPIO.output(Trigger, True)      # set Trigger to HIGH

    time.sleep(0.00001)
    GPIO.output(Trigger, False)     # set Trigger after 0.01ms to LOW

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(echo) == 0:
        StartTime = time.time()

    while GPIO.input(echo) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2

    print ("Measured Distance %d = %.1f cm" % (i, distance))

    return distance


seats = [False, False]
def seat(idx):
    global seats
    if seats[idx] == False:
        seats[idx] = True
        web.sit()

def unseat(idx):
    global seats
    if seats[idx]:
        seats[idx] = False
        web.unsit()

# Returns true if all chairs are occupied
def controlLED():  
    dist1 = distance(GPIO_TRIGGER, GPIO_ECHO, 1)
    dist2 = distance(GPIO_TRIGGER1, GPIO_ECHO1, 2)

    if dist1 < 30:
        animation(strip1, Color(0,0,0),10)
        seat(0)
    else:
        unseat(0)

    if dist2 < 30:
        animation(strip2, Color(0,0,0), 10)
        seat(1)
    else:
        unseat(1)


    if dist2 >= 30:
        animation(strip2, Color(255, 0, 0))
    if dist1 >= 30: 
        animation(strip1, Color(255, 0, 0))  
    if dist2 >= 30:
        animation(strip2, Color(0, 255, 0)) 
    if dist1 >= 30:
        animation(strip1, Color(0, 255, 0))  
    if dist2 >= 30:
        animation(strip2, Color(0, 0, 255)) 
    if dist1 >= 30:
        animation(strip1, Color(0, 0, 255))

    if (dist1 + dist2) <= 60:
        return True
    return False

def playMusic():
    p = vlc.MediaPlayer("~/makerlab/project/music.mp3")
    p.play()
    while controlLED:
        time.sleep(0.5)
    p.stop()
        

if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip1 = Adafruit_NeoPixel(LED_COUNT,   LED_PIN1,   LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip2 = Adafruit_NeoPixel(LED_COUNT,   LED_PIN2,   LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

    # Intialize the library (must be called once before other functions).
    strip1.begin()
    strip2.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            if controlLED():
                playMusic()

            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        if args.clear:
            animation(strip1, Color(0,0,0), 10)
            animation(strip2, Color(0,0,0), 10)

