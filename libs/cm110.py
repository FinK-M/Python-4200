import serial
from time import sleep
"""
--------------------------------------------------------------------------------
MODULE: cm110.py
WRITTEN IN: Python 3.4
DEPENDENCIES: pyserial, time.sleep
AUTHOR: Finlay TD Knops-Mckim
LAST MODIFIED: 2015/06/05
--------------------------------------------------------------------------------
This module contains a single class (and demo) for controlling the Specrtal
Products CM110 Compact Monochromator.

Example:
    >>import cm110.py
    >>M1 = cm110.mono(port=COM2)
    >>M1.command('goto', 5500)
    >>M1.close()

Information on the CM110 can be found at:
http://www.spectralproducts.com/cm110
--------------------------------------------------------------------------------
"""


class mono(object):

    """
    ----------------------------------------------------------------------------
    CLASS: mono
    INIT VARIABLES: port (str)
    INHERITANCE: Object
    ----------------------------------------------------------------------------
    An instance of this class represents a single monochromator. The user need
    only specify the port that the Monochromator is attached to, setup is taken
    care of in the __init__ method.

    All commands are sent via the command method, which takes two arguments.
    The first is the operation, a string, and the second (and optional third)
    are integers specifying the value sent with the operation.

    When the user is finished with sending commands they should call the close
    method to free up the serial port.
    ----------------------------------------------------------------------------
    """

    def __init__(self, port="COM1"):
        self.port = port
        self.setup_cm110()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.port)

    def __str__(self):
        return "Monochromator instance at %s" % self.port

    def setup_cm110(self):
        """
        ------------------------------------------------------------------------
        This method is called automatically by __init__ so there should be no
        need to call it manually unless you have previously called the close()
        method.
        ------------------------------------------------------------------------
        """
        self.cm = serial.Serial(
            port=self.port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )

    def command(self, operation, *args):
        """
        ------------------------------------------------------------------------
        *args should contain one argument except when the operation is:
        -reset, no arguments
        -scan, two arguments
        ------------------------------------------------------------------------
        """

        commands = {"calibrate": 18, "dec": 1, "echo": 27, "goto": 16,
                    "inc": 7, "order": 51, "query": 56, "reset": 255,
                    "scan": 12, "select": 26, "size": 55, "speed": 13,
                    "step": 54, "units": 50, "zero": 52}

        c = commands[operation.lower()]
        if c != 255:
            x = args[0]

        if c in [51, 56, 26, 55, 50]:
            self.cm.write(chr(c).encode())
            self.cm.write(chr(x).encode())

        elif c in [18, 16, 13]:
            high, low = divmod(x, 0x100)

            self.cm.write(chr(c).encode())

            self.cm.write(chr(high).encode())
            self.cm.write(chr(low).encode())

        elif c in [1, 27, 7, 54, 57]:
            self.cm.write(chr(c).encode())

        elif c is 255:
            for i in range(3):
                self.cm.write(chr(255).encode())

        elif c is 12:
            y = args[1]
            s_high, s_low = divmod(x, 0x100)
            e_high, e_low = divmod(y, 0x100)

            self.cm.write(chr(c).encode())

            self.cm.write(chr(s_high).encode())
            self.cm.write(chr(s_low).encode())

            self.cm.write(chr(e_high).encode())
            self.cm.write(chr(e_low).encode())

    def close(self):
        """
        ------------------------------------------------------------------------
        Call when finished with commands to free serial port
        ------------------------------------------------------------------------
        """
        self.cm.close()

if __name__ is "__main__":
    """
    ----------------------------------------------------------------------------
    Demo program to verify function:
    1) Creates a Monochromator instance at port "COM1".
    2) Runs a sweep from 390nm to 700nm and back again.
    3) Closes the port.
    ----------------------------------------------------------------------------
    """

    cm = mono(port="COM1")
    cm.setup_cm110()

    for i in range(3900, 7000, 100):
        cm.command("goto", i)
        sleep(0.5)

    sleep(2)

    for i in range(7000, 3900, -100):
        cm.command("goto", i)
        sleep(0.5)

    cm.close()
