#!/usr/bin/python
# -*- coding: utf-8 -*-
""" TinyG_tester.py - Test runner for functional and regression testing TInyG v8

    pyserial must be installed first - run this from term window: 
    sudo easy_install pyserial

    Build 001 - Basic functionality
"""
import sys, os, re
import glob
import serial
import random
import json
import time

### Helpers ###

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    for p in result:
        if p.find("usbserial") != -1:
            print p
            return p
        else:
            pass
    return None

def walk(top, func, arg):
    """ Local version of the os.path.walk routine """
    try:
        names = os.listdir(top)
    except os.error:
        return
#    names = names.sort()
    func(arg, top, names)           # Call out to the function that was passed in
    exceptions = ('.', '..')
    for name in names:
        if name not in exceptions:
            name = os.path.join(top, name)
            if os.path.isdir(name):
                walk(name, func, arg)

################################# MAIN PROGRAM BODY ###########################################

def main():

### Configuration ###

    CONFIGFILE = "tests_to_run.cfg"
    OUTFILE = "outfile.txt"

### Initialization ###

    # Locate and open the serial port
    ports =  serial_ports()
    if (ports):                     #We found a port
        port = serial.Serial(ports,115200,rtscts=1)
        
        if (not port.isOpen):
            print("Could not open serial port: \"%s\"" % ports)
            sys.exit(1)
        else:
            print("Serial Port Opened: %s" % port.portstr)
            
    else:
        print("Did not find a serial port" % ports)
        sys.exit(1)

    # Open the config file
    testrootpath = os.path.normpath(os.path.join(".",CONFIGFILE))
    try:
        testroots = open(testrootpath, "r" "utf8")
    except:
        print ("Could not open test config file: \"%s\"" % testrootpath)
        port.close()
        sys.exit(1)

### Main Routine ###

    for testroot in testroots:

        print("Starting tests in %s" % testroot)

        port.write("G0x0y0\n")
        port.write("m3\n")
        port.write("G0x10y10\n")
        port.writelines("g0x0y0\n")

    print("Done\n")

if __name__ == "__main__":
    main()
