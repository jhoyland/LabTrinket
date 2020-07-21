# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 17:51:22 2020

@author: James Hoyland
"""


import serial
import time

class LabTrinket:
    
    cmdADCDelay = "adc@delay={:.4f}\r"
    cmdADCVolts = "adc@mode={}\r"
    cmdADCNow = "adc!\r"
    cmdADCRun = "adc@run\r"
    cmdADCStop = "adc@stop\r"
    
    cmdLEDcolor = "led#{:02X}{:02X}{:02X}\r"
    cmdLEDbright = "led%{:}\r"
    cmdLEDoff = "led%0\r"
    
    rgbString = ""
    
    def __init__(self,connection):
        self.connection = connection
        self.value = 0
        self.dly = 1
        self.volts = False
        self.red = 0
        self.green = 0
        self.blue = 0
        self.brightness = 0
     
    
    def adcRequestValue(self):
        self.connection.write(LabTrinket.cmdADCNow.encode())
        
    def adcValueReady(self):
        return self.connection.in_waiting > 0
    
    # CircuitPython's "input" method echoes the serial sent to the board. So we have to strip out these echoes from the response
    
    def adcGetValue(self):
        success = False
        while self.adcValueReady() and not success:
            response = self.connection.readline()
            responseText = response.decode('ascii')
            if responseText[0] == '>':
                if responseText[1] == 'i':
                    self.value = int(responseText[2:])
                    success = True
                elif responseText[1] == 'v':
                    self.value = float(responseText[2:])
                    success = True
                    
        return success
    
    def adcSetOptions(self):
        
        self.connection.write((LabTrinket.cmdADCDelay.format(self.dly)).encode())
        if self.volts:
            self.connection.write((LabTrinket.cmdADCVolts.format("volts")).encode())
        else:
            self.connection.write((LabTrinket.cmdADCVolts.fromat("raw")).encode())
            
    def adcRun(self):
        self.adcSetOptions()
        self.connection.write(LabTrinket.cmdADCRun.encode())
        self.connection.reset_input_buffer()
        
    def adcStop(self):
        self.connection.write(LabTrinket.cmdADCStop.encode())
    
    def ledSetColor(self):
        self.connection.write((LabTrinket.cmdLEDcolor.format(self.red,self.green,self.blue)).encode())
        
    def ledSetBrightness(self):
        self.connection.write((LabTrinket.cmdLEDbright.format(self.brightness)).encode())
        
    def ledOn(self):
        self.ledSetBrightness()
        self.ledSetColor()
        
    def ledOff(self):
        self.connection.write(LabTrinket.cmdLEDoff.encode())
    
    


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

        
        
        
        
        
        

