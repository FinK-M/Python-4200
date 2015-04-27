import serial
from time import sleep

cm110 = serial.Serial(
		port="COM1",
		baudrate=9600,
		bytesize=serial.EIGHTBITS,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE
		)

def command(mono, operation, x=None, y=None):

	commands = {"calibrate": 18, "dec": 1, "echo": 27, "goto": 16, "inc": 7,
				"order": 51, "query": 56, "reset": 255, "scan": 12, "select": 26,
				"size": 55, "speed": 13, "step": 54, "units": 50, "zero": 52
				}

	c = commands[operation.lower()]

	if c in [51, 56, 26, 55, 50]:
		mono.write(chr(c).encode())
		mono.write(chr(x).encode())

	elif c in [18, 16, 13]:
		high, low = divmod(x, 0x100)

		mono.write(chr(c).encode())

		mono.write(chr(high).encode())
		mono.write(chr(low).encode())

	elif c in [1, 27, 7, 54, 57]:
		mono.write(chr(c).encode())

	elif c is 255:
		for i in range(3):
			mono.write(chr(255).encode())

	elif c is 12:
		s_high, s_low = divmod(x, 0x100)
		e_high, e_low = divmod(x, 0x100)

		mono.write(chr(c).encode())

		mono.write(chr(s_high).encode())
		mono.write(chr(s_low).encode())

		mono.write(chr(e_high).encode())
		mono.write(chr(e_low).encode())

if __name__ is "__main__":
	
	for i in range(3900, 7000, 100):
		command(cm110, "goto", i)
		sleep(0.5)

	sleep(2)

	for i in range(7000, 3900, -100):
		command(cm110, "goto", i)
		sleep(0.5)
