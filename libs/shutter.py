import serial
from time import sleep
"""
--------------------------------------------------------------------------------
MODULE: shutter.py
WRITTEN IN: Python 3.4
DEPENDENCIES: pyserial, time.sleep
AUTHOR: Finlay TD Knops-Mckim
LAST MODIFIED: 2015/06/05
--------------------------------------------------------------------------------
This module contains a single class (and demo) for controlling a simple Arduino
shutter system. The system in question consists of a servo motor with a
rectangular panel attached to it. The Arduino sets the servo to 90° when it
recieves a serial '1', and 0° with serial '0'. The shutter will not move
instantly and the methods have delays to reflect this, so take this into
account if precise timings are needed.

Example:
    >>import shutter.py
    >>S1 = ard_shutter(port=COM12)
    >>S1.open()
    >>S1.close()
    >>S1.shutdown()

Below is the code uploaded to the Arduino Uno.
--------------------------------------------------------------------------------
#include <Servo.h>

Servo myservo;
char p = '-1';
char last_p = '-1';

void setup()
{
  myservo.attach(9);
  Serial.begin(9600);
}

void loop()
{
  delay(50);
  if (Serial.available())
  {
    p = Serial.read();
    if(p != last_p)
    {
      if (p == '0')
      {
        myservo.write(0);
        Serial.println("Open");
      }
      else if (p == '1')
      {
        myservo.write(90);
        Serial.println("Closed");
      }
      else if (p == 'q')
      {
        Serial.println("Shutter");
      }
      last_p = p;
    }
    delay(50);
  }
}
--------------------------------------------------------------------------------
"""


class ard_shutter(object):

    """
    ----------------------------------------------------------------------------
    CLASS: ard_shutter
    INIT VARIABLES: port (str)
    INHERITANCE: Object
    ----------------------------------------------------------------------------
    An instance of this class represents a single Arduino Uno. The user need
    only specify the port that it is attached to, setup is taken care of in the
    __init__ method.

    There are three main methods in this class:
    -open() sets the servo motor to the 0 position, which should be adjusted to
     mean the shutter is open.
    -close() sets the servo to the 90 position, which should correspond to a
     closed shutter.
    -shutdown() terminates the serial session for the port in use.

    When the user is finished with sending commands they should call the
    shutdown method to free up the serial port.
    ----------------------------------------------------------------------------
    """

    def __init__(self, port="COM12"):
        """
        ------------------------------------------------------------------------
        The 2 second wait is due to the Arduino resetting when a new serial
        session is opened. 2 seconds is a rough estimate, it is worth checking
        the exact time with your own board.
        ------------------------------------------------------------------------
        """
        self.port = port
        self.shutter = serial.Serial(port=self.port)
        sleep(4)
        self.shutter.flush()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.port)

    def __str__(self):
        return "Arduino shutter instance at %s" % self.port

    def query(self):
        """
        ------------------------------------------------------------------------
        This function will query the session by sending the character "q".
        If the shutter is present the reply will be "Shutter" amd the function
        returns true, else returns false.
        ------------------------------------------------------------------------
        """
        self.shutter.write(b'q')
        sleep(0.1)
        status = self.shutter.read(self.shutter.inWaiting()).decode()
        correct = True if "Shutter" in status else False
        return correct

    def open(self):
        """
        ------------------------------------------------------------------------
        The time taken to move the shutter will depend on the exact servo and
        panel combination used. 1 second was about right for this experiment.
        ------------------------------------------------------------------------
        """
        self.shutter.write(b'0')
        sleep(1)  # wait for movement
        status = self.shutter.read(self.shutter.inWaiting())
        return status.decode().strip("\r\n")

    def close(self):
        """
        ------------------------------------------------------------------------
        As above, closing speed will change with equipment. And gravity if you
        are going the other way.
        ------------------------------------------------------------------------
        """
        self.shutter.write(b'1')
        sleep(1)  # wait for movement
        status = self.shutter.read(self.shutter.inWaiting())
        return status.decode().strip("\r\n")

    def shutdown(self):
        """
        ------------------------------------------------------------------------
        Call when finished with commands to free serial port
        ------------------------------------------------------------------------
        """
        self.shutter.close()


if __name__ == "__main__":
    """
    ----------------------------------------------------------------------------
    Demo program to verify function:
    1) Creates a Shutter instance at port "COM12".
    2) Opens the shutter, waits 2 seconds, closes the shutter.
    3) Closes the port.
    ----------------------------------------------------------------------------
    """
    sleep(4)
    sh = ard_shutter("COM13")
    print("Shutter detected: {0}".format(sh.query()))
    print(sh.open())
    sleep(2)
    print(sh.close())
    sh.shutdown()
