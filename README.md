# LabTrinket
A system for using a Trinket M0 as a simple lab instrument interface for take-home experiments

The LabTrinket is based on the Trinket M0 microcontroller from Adafruit. It is designed to use the Tinket as a low cost component for take-home science labs allowing data gathering and some control of experiments. The Trinket is run connected to a host computer and responds to simple serial commands over USB. There are two parts. 

In the directory CIRCUIT PYTHON the file main.py is the loaded onto the Trinket. This handles commands from the host.
The file labtrinket.py is the class library for the host computer. It encapsulates the serial control for the Trinket.
The Jupyter Notebook  TrinketExperiment is a tutorial to walk through the main features

