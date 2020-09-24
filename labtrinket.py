# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 17:51:22 2020

@author: James Hoyland

LabTrinket:
    
This class encapsulates serial communications with the Trinket M0 running the lab trinket python code.

Through this interface you can set LED color and brightness, get ADC values and control the PWM and true analog output on the board.


"""


import serial
import time

class LabTrinket:
    
    #Command strings for Trinket M0
    
    cmdADCDelay = "adc@delay={:.4f}\r"
    cmdADCVolts = "adc@mode={}\r"
    cmdADCNow = "adc!\r"
    cmdADCRun = "adc@run\r"
    cmdADCStop = "adc@stop\r"
    
    cmdDACOn = "dac@on\r"
    cmdDACOff = "dac@off\r"
    cmdDACLevel ="dac@level={:}\r"
    
    cmdLEDcolor = "led#{:02X}{:02X}{:02X}\r"
    cmdLEDbright = "led%{:}\r"
    cmdLEDoff = "led%0\r"
    
    def __init__(self,connection):
        self.connection = connection
        self.value = 0
        self.dly = 1 #delay in seconds between ADC measurements when free running
        self.volts = False  #by default 
        #Some default settings for LED so ledOn does something if used right away
        self.red = 128
        self.green = 0
        self.blue = 0
        self.brightness = 100
     
    
    #grabs an ADC value. Note, unless adcWriteOptions is called first the ADC settings will be as currently set on the board
    #not necessarily the values stored in the LabTrinket instance. If the Trinket has been set into free running mode
    #using adcRun then this has already been done
        
    def adcRequestValue(self):
        self.connection.write(LabTrinket.cmdADCNow.encode())
        
    def adcValueReady(self):
        return self.connection.in_waiting > 0
    
    # CircuitPython's "input" method echoes the serial sent to the board. 
    # So we have to strip out these echoes from the response
    # Correct board response begins with '>'
    
    def adcGetValue(self,tries=50):
        success = False
        while self.adcValueReady() and not success and tries>0:
            response = self.connection.readline()
            responseText = response.decode('ascii')
            if responseText[0] == '>':
                if responseText[1] == 'i':
                    self.value = int(responseText[2:])
                    success = True
                elif responseText[1] == 'v':
                    self.value = float(responseText[2:])
                    success = True
            tries = tries - 1
                    
        return success
    
    def adcWriteOptions(self):
        
        self.connection.write((LabTrinket.cmdADCDelay.format(self.dly)).encode())
        if self.volts:
            self.connection.write((LabTrinket.cmdADCVolts.format("volts")).encode())
        else:
            self.connection.write((LabTrinket.cmdADCVolts.format("raw")).encode())
            
    def adcRun(self):
        self.adcWriteOptions()
        self.connection.write(LabTrinket.cmdADCRun.encode())
        self.connection.reset_input_buffer()
        
    def adcStop(self):
        self.connection.write(LabTrinket.cmdADCStop.encode())
        
    """adcVoltMode: Sets the Trinket ADC to "volt" mode. In this case ADC values are converted to actual voltages and 
    sent as a floating point number. Otherwise the ADC returns the raw ADC integer (12-bit value)  """
    
    def adcVoltMode(self,mode=True):
        self.volts = mode
        if self.volts:
            self.connection.write((LabTrinket.cmdADCVolts.format("volts")).encode())
        else:
            self.connection.write((LabTrinket.cmdADCVolts.format("raw")).encode())
            
    def adcDelay(self,delay=1):
        self.dly = delay
        self.connection.write((LabTrinket.cmdADCDelay.format(self.dly)).encode())   
        
        
    def dacOn(self):
        self.connection.write(LabTrinket.cmdDACOn.encode())
        
    def dacOff(self):
        self.connection.write(LabTrinket.cmdDACOff.encode())
        
    def dacLevel(self,level):
        self.connection.write((LabTrinket.cmdDACLevel.format(level)).encode())
        
    def dacVolts(self,volts):
        if volts > 3.3:
            volts = 3.3
        if volts < 0:
            volts = 0
            
        level = int(65536 * volts / 3.3)
        
        self.dacLevel(level)
        
    
    #Set RGB values for NeoStar LED, ignores values which are out of range
    
    def ledSetColor(self,red=-1, green = -1, blue = -1, writeToTrinket = True):
        if red >= 0 and red < 256:
            self.red = red
        if green >= 0 and green < 256:
            self.green = green
        if blue >= 0 and blue < 256:
            self.blue = blue
            
        if writeToTrinket:
            self.connection.write((LabTrinket.cmdLEDcolor.format(self.red,self.green,self.blue)).encode())
        
    def ledSetBrightness(self, brightness = -1, writeToTrinket = True):
        
        if brightness >= 0 and brightness <= 100:
            self.brightness = brightness
        
        if writeToTrinket:
            self.connection.write((LabTrinket.cmdLEDbright.format(self.brightness)).encode())
        
    def ledOn(self):
        self.ledSetBrightness()
        self.ledSetColor()
        
    def ledOff(self):
        self.connection.write(LabTrinket.cmdLEDoff.encode())
    
    
if __name__ == "__main__":

    serconn = serial.Serial()
    serconn.port = 'COM17'
    serconn.baudrate = 9600
    serconn.open()
    
    trinket = LabTrinket(serconn)
    
    i = 0
    
    trinket.volts = True
    trinket.delay = 0.5
    
    trinket.red = 250
    trinket.green = 12
    trinket.blue = 112
    
    trinket.brightness = 75
    
    trinket.ledOn()
    
    trinket.adcRun()
    
    while i<50:
        if trinket.adcGetValue():
            print("{}: {}".format(i,trinket.value))
            i = i+1
            trinket.green += 2
            trinket.red -= 4
            trinket.ledSetColor()
    
    
    print("Done")
    
    trinket.adcStop()
    
    trinket.ledOff()
    
    serconn.close()

        
        
        
        
        
        

