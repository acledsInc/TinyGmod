#!/usr/bin/python
# -*- coding: utf-8 -*-
""" TinyG_tester.py - Test runner for functional and regression testing TInyG v8

    pyserial must be installed first - run this from term window: 
    sudo easy_install pyserial

    TinyG_tester.py build 003 - Runs a simple test from a root directory
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


def nonblocking_readlines(f):
    """Generator which yields lines from F (a file object, used only for its fileno())
       without blocking.  If there is no data, you get an endless stream of empty
       strings until there is data again (caller is expected to sleep for a while).
       Newlines are normalized to the Unix standard.

       Reference: http://code.activestate.com/recipes/578900-non-blocking-readlines/
    """

    fd = f.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    enc = locale.getpreferredencoding(False)

    buf = bytearray()
    while True:
        try:
            block = os.read(fd, 8192)
        except BlockingIOError:
            yield ""
            continue

        if not block:
            if buf:
                yield buf.decode(enc)
                buf.clear()
            break

        buf.extend(block)

        while True:
            r = buf.find(b'\r')
            n = buf.find(b'\n')
            if r == -1 and n == -1: break

            if r == -1 or r > n:
                yield buf[:(n+1)].decode(enc)
                buf = buf[(n+1):]
            elif n == -1 or n > r:
                yield buf[:r].decode(enc) + '\n'
                if n == r+1:
                    buf = buf[(r+2):]
                else:
                    buf = buf[(r+1):]

def walk(top, func, args):
    """ Local version of the os.path.walk routine """

    try:
        names = os.listdir(top)
    except os.error:
        print ("directory not found: %s" % top)
        return

    names.sort()                        # sort the list so it agrees with the user's directory listing
    exceptions = ('.', '..', '.DS_Store')
    for name in names:
        if name in exceptions:
            continue

        if os.path.isdir(name):
            walk(name, func, args)
        else:
            func(args, top, name)       # Call out to the function that was passed in


def test_runner(args, top, name):
    """ Run a single test file """

    port = args[0]                      # listed for redability
    outfile = args[1]
    action = args[2]

    filepath = os.path.normpath(os.path.join(top, name))
    try:
        testfile = open(filepath, "r" "utf8")
        print ("Running %s" % filepath)
    except:
        print ("Could not open test file: \"%s\"" % filepath)
        return

    lines = testfile.readlines()        # read line including newline at end
    for line in lines:
#        print line[:-1]
        port.write(line)
#        response = port.readlines()
#        if (response == "\n"):
#        if (response == None):
#            continue
#        print response

    response = port.readlines()
    print response
    
################################# MAIN PROGRAM BODY ###########################################

def main():

### Configuration ###

    ROOTDIR = "."
    CONFIGFILE = "tests_to_run.cfg"
    OUTFILE = "outfile.txt"
    ACTION = True                   # Set to false for dry run

### Initialization ###

    os.chdir(".")                   # Set current working directory to root so paths come out right
    

    ### Open the config file
    
    testrootpath = os.path.normpath(os.path.join(ROOTDIR, CONFIGFILE))
    try:
        testroots = open(testrootpath, "r" "utf8")
    except:
        print ("Could not open test config file: \"%s\" - EXITING" % testrootpath)
        sys.exit(1)

    ### Open the output file

    outfilepath = os.path.normpath(os.path.join(ROOTDIR, OUTFILE))
    try:
        os.remove(outfilepath)
    except:
        pass
    outfile = open(outfilepath,"a+w")

    ### Locate and open the serial port

    ports =  serial_ports()

    if (not ports):
        print("Did not find a serial port - EXITING")
        testroots.close()
        sys.exit(1)
    else:
        port = serial.Serial(ports, 115200, timeout=0, rtscts=1)    # open for non-blocking reads
        if (not port.isOpen):
            print("Could not open serial port: \"%s\" - EXITING" % ports)
            testroots.close()
            sys.exit(1)
        else:
            print("Serial Port Opened: %s" % port.portstr)

### Main Routine ###

    args = (port, outfile, ACTION)

    for testroot in testroots:

        testroot = testroot[:-1]
        print("Starting tests in %s" % testroot)
        walk(os.path.join(ROOTDIR, testroot), test_runner, args)
#        walk(os.path.normpath(os.path.join(ROOTDIR, testroot)), test_runner, args)
#        walk(testroot, test_runner, args)
#        walk(".", test_runner, args)

    outfile.close()
    testroots.close()
    port.close()
    print("DONE\n")

if __name__ == "__main__":
    main()
