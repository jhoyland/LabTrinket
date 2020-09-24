# LabTrinket
# Allows control of the ADC, PWM and on board LED function of the Trinket M0 over serial using simple text commands.

# LED code based on ATMaker's Handup.

# This program uses the board package to access the Trinket's pin names
# and uses adafruit_dotstar to talk to the LED
# other boards would use the neopixel library instead

import time
import board
import adafruit_dotstar
import supervisor
from analogio import AnalogIn
from analogio import AnalogOut

# define pins

adc_pin = AnalogIn(board.D0)
dac_pin = AnalogOut(board.A0)

# setup initial state

# ADC

adc_running = False
adc_delay = 1.0
adc_mode = "raw"

# DAC

dac_running = False
dac_level = 30000
dac_pin.value = 0

# LED

pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=.95)
black = (0, 0, 0)
curColor = black
targetColor = black
led_mode = "off"
pixels.fill(black)
pixels.show()

# Timer

lastime = thistime = time.monotonic()

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

# Main Loop
while True:
    # Check to see if there's input available (requires CP 4.0 Alpha)
    if supervisor.runtime.serial_bytes_available:
        # input() will block until a newline is sent
        # input() echoes the received line back to the sender. This is a pain.
        inText = input().strip()
        # Sometimes Windows sends an extra (or missing) newline - ignore them
        if inText == "":
            continue

        # Process the input text - start with the presets (no #,@,etc)
        # We use startswith to not have to worry about CR vs CR+LF differences

        # LED commands

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
 

        # ADC commands

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

        # DAC commands

        elif inText.startswith("dac"):

            optTex = inText[3:]

            if optTex.startswith("@"):
                command = optTex[1:].split('=',1)

                if command[0] == "on":
                    dac_running = True
                    dac_pin.value = dac_level

                elif command[0] == "off":
                    dac_running = False
                    dac_pin.value = 0

                elif command[0] == "level":
                    v = int(command[1])
                    if v > 65535:
                        v = 65535
                    if v < 0:
                        v = 0

                    dac_level = v
                    if dac_running:
                        dac_pin.value = dac_level



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
