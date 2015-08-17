import serial
from time import sleep
"""
--------------------------------------------------------------------------------
MODULE: cm110.py
WRITTEN IN: Python 3.4
DEPENDENCIES: pyserial, time.sleep
AUTHOR: Finlay TD Knops-Mckim
LAST MODIFIED: 2015/08/15
--------------------------------------------------------------------------------
This module contains a single class (and demo) for controlling the Specrtal
Products CM110 Compact Monochromator.

Example:
    >>>import cm110.py              # import library
    >>>M1 = cm110.mono(port=COM2)   # monochromator at port COM2
    >>>M1.goto(5500)                # Goto 550nm, green light
    >>>M1.close()                   # Finish the session

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

    def __init__(self, port="COM1", debug=False):
        self.debug = debug
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

    def send(self, item):
        self.cm.write(chr(item).encode())
        sleep(0.01)

    def command(self, operation, *args):
        """
        ------------------------------------------------------------------------
        *args should contain one argument except when the operation is:
        -reset, no arguments
        -scan, two arguments
        ------------------------------------------------------------------------
        """

        self.cm.flush()
        commands = {"calibrate": 18, "dec": 1, "echo": 27, "goto": 16,
                    "inc": 7, "order": 51, "query": 56, "reset": 255,
                    "scan": 12, "select": 26, "size": 55, "speed": 13,
                    "step": 54, "units": 50, "zero": 52}

        try:
            c = commands[operation.lower()]
            x = args[0] if args else None
        except:
            print("Invalid command")

        self.send(c)

        if c in [51, 56, 26, 55, 50]:
            self.send(x)

        elif c in [18, 16, 13]:
            high, low = divmod(x, 0x100)

            self.send(high)
            self.send(low)

        elif c is 255:
            for i in range(2):
                self.send(255)

        elif c is 12:
            y = args[1]
            s_high, s_low = divmod(x, 0x100)
            e_high, e_low = divmod(y, 0x100)

            self.send(s_high)
            self.send(s_low)

            self.send(e_high)
            self.send(e_low)

    def close(self):
        """
        ------------------------------------------------------------------------
        Call when finished with commands to free serial port
        ------------------------------------------------------------------------
        """
        self.cm.close()

    def read_hi_lo(self):
        """
        ------------------------------------------------------------------------
        Interprets data received from the Monochromator in the format of a high
        and low byte. Also reads the status and message bytes. If the message
        byte is not equal to 24 the function returns -1 to signify an error.
        ------------------------------------------------------------------------
        """
        raw = []
        sleep(0.01)
        for j in range(self.cm.inWaiting()):
            raw += self.cm.read()
        data = int(hex(raw[0]) + hex(raw[1]).replace('0x', ''), 16)
        status = raw[2]
        message = raw[3]
        try:
            assert(message == 24)
            return data, status, message
        except AssertionError:
            return -1

    def message_status(self, raw=None):
        """
        ------------------------------------------------------------------------
        Reads in the status and message bits and
        ------------------------------------------------------------------------
        """
        if not raw:
            raw = []
            for j in range(self.cm.inWaiting()):
                raw += self.cm.read()
        status = raw[0]
        message = raw[1]
        stat_message = self.status(status)
        try:
            assert message == 24
            return stat_message
        except AssertionError:
            return -1

    def status(self, status):
        """
        ------------------------------------------------------------------------
        Takes a status byte and constructs a list of status messages based on
        the value of each bit.
        ------------------------------------------------------------------------
        """

        stat_message = ["Status byte is {0}".format(status)]

        # Check if command was accepted
        stat_message.append(
            ("Command accepted", "Command not accepted")
            [(status & 1 << 7) >> 7])

        # Does the command require action to rectify?
        stat_message.append(
            ("Requires action", "Requires no action")
            [(status & 1 << 6) >> 6])

        # Why was the command not accepted? Ignore if command accepted
        stat_message.append(
            ("Specifier was too large", "Specifier was too small")
            [(status & 1 << 5) >> 5])

        # Which way is the scan going?
        stat_message.append(
            ("Scan is positive going", "Scan is negative going")
            [(status & 1 << 4) >> 4])

        # Which order is the scan?
        stat_message.append(
            ("Positive orders", "Negative orders")
            [(status & 1 << 3) >> 3])

        # What units are being used?
        units = ("microns", "nanometers", "angstroms")
        stat_message.append("Units are " + units[status & 7])

        return stat_message

    def calibrate(self, position):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        print("CAUTION: Use of this command will erase factory settings!")
        proceed = input("(y/n) Do you still wish to proceed? ").lower()
        if proceed != "y":
            return 0
        else:
            self.command("calibrate", position)
            print(self.message_status())

    def dec(self):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("dec")
        print(self.message_status())

    def echo(self):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """

        self.command("echo")
        sleep(0.01)
        if chr(27) == self.cm.read().decode():
            return("Echo test succesful")
        else:
            return("No response recieved")

    def goto(self, wavelength):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("goto", wavelength)
        sleep(0.1)
        if self.debug:
            return self.message_status()
        else:
            return 0

    def inc(self):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("inc")
        print(self.message_status())

    def order(self, order):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("order")
        print(self.message_status())

    def query(self):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        print("CURRENT CONGIGURATION")
        print("=====================")
        properties = ("Position:",
                      "Type:",
                      "Grooves/mm:",
                      "Blaze:",
                      "Grating No:",
                      "Speed:",
                      "Size:",
                      "No. of Gratings:",
                      "Current Units:",
                      "Serial No.")
        q_bytes = list(range(7)) + [13, 14, 19]
        i = 0
        for q in q_bytes:

            self.cm.write(chr(56).encode())
            self.cm.write(chr(q).encode())
            raw = []
            sleep(0.01)
            try:
                for j in range(self.cm.inWaiting()):
                    raw += self.cm.read()
                data = int(hex(raw[0]) + hex(raw[1]).replace('0x', ''), 16)
            except:
                data = "Not recieved"
            print(properties[i], data)
            i += 1
        print("\nSTATUS BYTE REPORT")
        print("==================")
        for m in self.message_status(raw=[raw[2], raw[3]]):
            print(m)

    def reset(self):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("reset")
        print(self.message_status())

    def scan(self, start, end):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("scan", start, end)
        sleep(0.1)
        print(self.message_status())

    def speed(self, speed):
        """
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.command("speed", speed)
        sleep(0.01)
        print(self.message_status())

    def step():
        pass


if __name__ == "__main__":
    """
    ----------------------------------------------------------------------------
    Demo program to verify function:
    1) Creates a Monochromator instance at port "COM1".
    2) Runs a sweep from 390nm to 700nm and back again.
    3) Closes the port.
    ----------------------------------------------------------------------------
    """

    cm = mono(port="COM1")
    for i in range(3900, 7000, 100):
        cm.goto(i)
        sleep(0.1)

    sleep(2)

    for i in range(7000, 3900, -100):
        cm.goto(i)
        sleep(0.1)

    cm.close()
