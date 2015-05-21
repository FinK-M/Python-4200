import serial
from time import sleep


class ard_shutter(object):

    def __init__(self, port="COM12"):
        self.port = port
        self.shutter = serial.Serial(port=self.port)
        sleep(2)

    def open(self):
        self.shutter.write(b'0')
        sleep(1)  # wait for movement

    def close(self):
        self.shutter.write(b'1')
        sleep(1)  # wait for movement

    def shutdown(self):
        self.shutter.close()

if __name__ == "__main__":
    sh = ard_shutter("COM12")
    sh.open()
    sleep(2)
    sh.close()
    sh.shutdown()
