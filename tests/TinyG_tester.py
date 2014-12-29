#!/usr/bin/python
# -*- coding: utf-8 -*-
""" TinyG_tester.py - Test runner for functional and regression testing TInyG v8

    pyserial must be installed first - run this from term window: 
    sudo easy_install pyserial

    Build 002 - Interim commit
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

#    top = "./test_root"
#    top = "./" + top
#    print top

    abspath = os.path.abspath(top)
    print abspath

    try:
        names = os.listdir(abspath)
    except os.error:
        print os.error
        print ("directory not found: %s" % abspath)
        return
    print names
#    names = names.sort()
    func(arg, top, names)           # Call out to the function that was passed in
    exceptions = ('.', '..')
    for name in names:
        if name not in exceptions:
            name = os.path.join(top, name)
            if os.path.isdir(name):
                walk(name, func, arg)

def test_runner(args, top, names):
    
    print "Running Test"
    print args

    args[0].write("G0x0y0\n")
    args[0].write("m3\n")
    args[0].write("G0x10y10\n")
    args[0].writelines("g0x0y0\n")
    

################################# MAIN PROGRAM BODY ###########################################

def main():

### Configuration ###

    ROOTDIR = "."
    CONFIGFILE = "tests_to_run.cfg"
    OUTFILE = "outfile.txt"
    ACTION = True                   # Set to false for dry run

### Initialization ###

    os.chdir(".")                   # Set current working directory to root so paths come out right
    

    # Open the config file
    testrootpath = os.path.normpath(os.path.join(ROOTDIR, CONFIGFILE))
    try:
        testroots = open(testrootpath, "r" "utf8")
    except:
        print ("Could not open test config file: \"%s\" - EXITING" % testrootpath)
        sys.exit(1)

    # Locate and open the serial port
    ports =  serial_ports()

    if (not ports):
        print("Did not find a serial port - EXITING")
        testroots.close()
        sys.exit(1)
    else:
        port = serial.Serial(ports,115200,rtscts=1)
        if (not port.isOpen):
            print("Could not open serial port: \"%s\" - EXITING" % ports)
            testroots.close()
            sys.exit(1)
        else:
            print("Serial Port Opened: %s" % port.portstr)

    # Open a unique output file
    outfilepath = os.path.normpath(os.path.join(ROOTDIR, OUTFILE))
    try:
        os.remove(outfilepath)
    except:
        pass
    outfile = open(outfilepath,"a+w")

### Main Routine ###

    args = (port, outfile, ACTION)

    for testroot in testroots:

        print("Starting tests in %s" % testroot)
#        walk(os.path.join(ROOTDIR, testroot), test_runner, args)
#        walk(os.path.normpath(os.path.join(ROOTDIR, testroot)), test_runner, args)
#        walk(testroot, test_runner, args)
        walk(".", test_runner, args)

    outfile.close()
    testroots.close()
    port.close()
    print("DONE\n")

if __name__ == "__main__":
    main()
