# LabTrinket
# Allows control of the ADC, PWM and on board LED function of the Trinket M0 over serial using simple text commands.
# LED code based on ATMaker's Handup.


# ATMakers HandUp
# Listens to the USB Serial port and responds to incoming strings
# Sets appropriate colors on the DotStar LED

# This program uses the board package to access the Trinket's pin names
# and uses adafruit_dotstar to talk to the LED
# other boards would use the neopixel library instead

import time
import board
import adafruit_dotstar
import supervisor
from analogio import AnalogIn

# create an object for the dotstar pixel on the Trinket M0
# It's an array because it's a sequence of one pixel
pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=.95)

adc_pin = AnalogIn(board.D0)
adc_running = False
adc_delay = 1.0
# this function takes a standard "hex code" for a color and returns
# a tuple of (red, green, blue)
def hex2rgb(hex_code):
    red = int("0x"+hex_code[0:2], 16)
    green = int("0x"+hex_code[2:4], 16)
    blue = int("0x"+hex_code[4:6], 16)
    rgb = (red, green, blue)
    # print(rgb)
    return rgb

# sends a value on serial connection. All transmissions are prefixed with '>' to make it easier for host computer application
# to sort out Trinket transmissions from the echo resulting from the input() commands (see below).

def sendValue(v):
    if adc_mode == "volts":				# Convert the ADC value to volts
        fv = (v*3.3) / 65536
        print(">v%0.5f" % fv)
    else:
        print(">i%d" % v)				# Send raw ADC value


# When we start up, make the LED black
black = (0, 0, 0)
curColor = black
targetColor = black
led_mode = "off"
adc_mode = "raw"

# Initialize the timer
lastime = thistime = time.monotonic()

# We start by turning off pixels
pixels.fill(black)
pixels.show()



# Main Loop
while True:
    # Check to see if there's input available (requires CP 4.0 Alpha)
    if supervisor.runtime.serial_bytes_available:
        # read in text (@mode, #RRGGBB, %brightness, standard color)
        # input() will block until a newline is sent
        # input() echoes the received line back to the sender. This is a pain.
        inText = input().strip()
        # Sometimes Windows sends an extra (or missing) newline - ignore them
        if inText == "":
            continue
        # Process the input text - start with the presets (no #,@,etc)
        # We use startswith to not have to worry about CR vs CR+LF differences

        elif inText.startswith("led"):

            optText = inText[3:]
            # Here we can set the brightness with a "%" symbol
            if optText.startswith("%"):
                pct = float(optText[1:])/100.0
                pixels.brightness=pct
                led_mode = 'solid'
            # If we get a hex code set it and go to solid
            elif optText.startswith("#"):
                targetColor = hex2rgb(optText[1:])
                led_mode = 'solid'
            # Otherwise flash the led red
            else:
                targetColor= (50,0,0)
                led_mode = 'blink'
 

        elif inText.startswith("adc"):

            optText = inText[3:]
            # adc! gets an instantaneous ADC value
            if optText.startswith("!"):
            	led_mode = 'solid'
                sendValue(adc_pin.value)

            # Other ADC options These are in the format  @param=value
            if optText.startswith("@"):
                command = optText[1:].split('=',1)
                # Start streaming an ADC sequence
                if command[0] == "run":
                    adc_running = True
                    lastime = time.monotonic()
                # Stop streaming
                elif command[0] == "stop":
                    adc_running = False
                # Set the delay for free running ADC
                elif command[0] == "delay":
                    adc_delay = float(command[1])
                # Set the ADC mode (volts or raw)
                elif command[0] == "mode":
                    adc_mode = command[1]

        else:
            targetColor =(0, 0, 50)
            led_mode="blink"

    else:
        # If no text available, update the color according to the mode
        if led_mode == 'blink':
            if curColor == black:
                curColor = targetColor
            else:
                curColor = black
            time.sleep(.4)
            # print('.', end='')
            pixels.fill(curColor)
            pixels.show()
        elif led_mode == 'solid':
            pixels.fill(targetColor)
            pixels.show()
        else:
            pixels.fill(black)
            pixels.show()

        if adc_running:
            thistime = time.monotonic()
            if thistime - lastime > adc_delay:
                sendValue(adc_pin.value)
                lastime = thistime
