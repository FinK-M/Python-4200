# Python-4200
## Introduction
This project aims to use python to control several pieces of laboratory test equipment as part of a characterisation system for Indium Oxide semiconductors. This is achieved by using the PyVisa library to control the instruments via GPIB and serial interfaces. The primary instrument is the Keithley 4200-SCS (Semiconductor Characterisation System), a powerful device for running a range of automated tests using Source Measurment Units (SMUs), Capacitance Voltage Units (CVUs), and Pulse Measurement Units (PMUs).
## Script Details
The script Python_4200.py provides a simple text based interface for running tests on the 4200-SCS. The user is presented with a list of available devices, and can then choose a test to run. The results are displayed via matplotlib and saved to csv files in the script directory.

Python_5302.py is a preliminary script to communicate with an EG&G lock in amplifier, another part of the experimental set-up.
