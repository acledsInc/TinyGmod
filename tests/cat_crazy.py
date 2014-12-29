#!/usr/bin/python
""" Example program for serial communication to TinyG
    pyserial must be installed first - run this from term window: 
    sudo easy_install pyserial

    Build 001 - Modified cat_crazy.py as serial example file for FTDI-based devices (v8)
"""
import sys
import glob
import serial
import random
from time import sleep

from decimal import Decimal
TWOPLACES = Decimal(10) ** -2

"""This is my cat's play toy"""

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
        
MAX_X = 2000
MAX_Y = 200
MIN_X = -2000
MIN_Y = 100
MAX_FEED = 255000
MIN_FEED = 155000

MIN_DELAY = .05 #quarter second
MAX_DELAY = .25 #2 seconds
LOOPS = 10000

def meow():
    x = random.randint(MIN_X,MAX_X)
    y = random.randint(MIN_Y,MAX_Y)
    feed = random.randint(MIN_FEED,MAX_FEED)
    delay = Decimal(random.uniform(MIN_DELAY, MAX_DELAY)).quantize(TWOPLACES)

    print("Meow %d %d" % (x, y))
    return(feed, delay, x,y)

def main():
    print("Starting the Cat Crazy")
    
    glowWriter =  serial_ports()
    if(glowWriter):
        #We found a port
        s = serial.Serial(glowWriter,115200,rtscts=1)
        
        if(not s.isOpen):
            print("Could not open serial port %s " % glowWriter)
            sys.exit(1)
        else:
            #We are open and ready to rock the kitty time.
            print("Serial Port Opened: %s" % s.portstr)
            s.write("G0x0y0\n")
            s.write("m3\n")
            s.write("G0x10y10\n")
            
            """ Comment out the cat crazy stuff that would crash your machine
            for x in range(0,LOOPS):
                tmpfeed, tmpdelay, tmpx, tmpy = meow()
                s.write("G4P%s\n" % tmpdelay)
                s.write("g1F%s X%s Y%s\n" % (tmpfeed, tmpx, tmpy))
                sleep(tmpdelay)
            """
            s.writelines("g0x0y0\n")

    print("Done\n")

if __name__ == "__main__":
    main()
