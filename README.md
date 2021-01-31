# Introducing the LabTrinket

The LabTrinket is based on the Trinket M0 microcontroller from Adafruit. It is designed to use the Tinket as a low cost component for take-home science labs allowing data gathering and some control of experiments. The Trinket is run connected to a host computer and responds to simple serial commands over USB. LabTrinket consists of two parts. 
1) A Circuit Python script to place on the Trinket microcontroller to interpret and execute serial commands from the host computer
2) A python library for the host computer to allow it to communicate with the Trinket

## Setting up the First Time

### Windows Drivers

For Windows you will need to download and install drivers from here: https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino/windows-driver-installation  This step is not needed for Linux or MacOS. Follow the instructions at that link.

### Circuit Python

Connect the Board via the USB. You should see some LEDs flash on the board and you will notice the Trinket appears as an external drive on your computer, like a flash drive. 

The Trinket M0 uses an onboard Python interpreter called CircuitPython. Before first use you will need to update to the latest version. Visit this section: https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino?view=all#what-is-circuitpython and follow the instructions _very carefully_ to install the latest version on the Trinket.

### LabTrinket Code

The LabTrinket client code is called "main.py" can be found in the "CircuitPython" folder of this repo. https://github.com/jhoyland/LabTrinket 
After you have updated CircuitPython and restarted your Trinket (by plugging it out and in again) you can copy main.py onto it. It will overwrite the main.py which is already on your Trinket. 

### Install LED Libraries
The Circuit Python on the Trinket needs a couple of libraries to operate the on board LED. You can get hold of the complete bundle of libraries from https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20200925 You probably installed CircuitPython 5 in the earlier step so get version 5 of the bundle. Unzip this somewhere convenient. 
From the bundle you need two libraries:
```
adafruit_dotstar.mpy
adafruit_pypixelbuf.mpy
```
On your Trinket there should be a folder called \lib  (you can create one if it's not there)  Copy the two libraries into the lib folder on the Trinket. That's the whole install for the Trinket itself. You don't need the rest of the bundle you just unzipped and it can be deleted if you want to save space.

### Install PySerial

You need one last bit of install. The base Anaconda installation does not include the serial communications package. To install, you need to start up an "Ananconda Prompt" - on Windows this is on the Start Menu under "Anaconda". There you can type: ```conda install -c anaconda pyserial```
Follow the on screen instructions. This should install the latest version. If not using Anaconda use pip or equivalent to install pyserial

## Test your Trinket!

Provided in this repo is a Jupyter Notebook to test the specific features of the LabTrinket. You can also run labtrinket.py directly for a demonstration

## Basic operation

To use labtrinket from python 

```python
import labtrinket
import serial
```

You must first setup the serial connection e.eg

```python
ser = serial.Serial()
ser.port = 'YOUR_SERIAL_PORT'
ser.baudrate = 9600
ser.open()
```

Here `YOUR_SERIAL_PORT` is whatever port your Trinket is connected to.

With the serial port connected you can create a labtrinket object and associate it with the serial connection.

```python
trinket = labtrinket.LabTrinket(ser)
```

Lab trinket commands:

### Controlling onboard LED

```python
ledSetColor(red=r,green=g,blue=b)
```
Sets LED color. Where r,g and b are integers from 0-255 for the LED red,greed and blue colors

```python
ledSetBrightness(n)
```

Sets LED brightness to n. Where n is a percentage of maximum

```python
ledOn()
```

Turns the LED on with the last RGB and brightness values

```python
ledOff()
```

Turns the LED off

### Using the ADC

```python
adcRequestValue()
```

Requests a single value from the Trinket. The function does not wait for the value. The Trinket reads the ADC value and returns it when ready. You must use adcGetValue to obtain the value from the serial buffer.

```python
adcGetValue(tries=n)
```
Will try n times to get an ADC value from the serial buffer. Returns true if successful. The value itself is stored in the 'value' field of LabTrinket object. You can access this like:

```python
x = trinket.value
```

```python
adcRun()
```

Sets the Trinket ADC into "free-running" mode where it continually requests new values at a fixed rate. You receive these by continually calling adcGetValue

```python
adcStop()
```

Ends free running mode. Values may remain in the serial buffer so you should either flush it or poll it with adcGetValue until empty

```python
adcAveragedValue(n)
```

Takes n readings from the ADC and returns the mean value

```python
adcDelay(d)
```

Sets the time in seconds of the delay between measurements in free running or averaged mode. Default value is 1 second.


### Controlling the DAC

```python
dacOn()
```

Turns on the True DAC on pin 1 of the Trinket M0.

```python
dacOff()
```

Turns off the DAC


```python
dacVolts(v)
```

Sets the DAC voltage to v. Will not let you set a voltage higher than 3.3V






