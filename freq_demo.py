import visa
from time import sleep
from Python_4200 import select_device

rm = visa.ResourceManager()
#addr = select_device(rm)
addr = 'GPIB0::3::INSTR'
instr = rm.open_resource(addr)

for i in range(0, 401, 25):
    Vout = (i - 2.1333)/42.139
    instr.write("VSET " + str(Vout))
    print(str(i) + " Hz " + str(Vout) + " V")
    sleep(5)

instr.write("VSET 0")

"""
Vout = 0
while True:
    try:
        freq = int(input("Enter a freq between 40 and 400Hz: "))
        if freq < 40 or freq > 400:
            raise ValueError
        else:
            Wait = 10/freq
            Vout = float((freq - 2.1333)/42.139)
            instr.write("VSET " + str(Vout))
    except ValueError:
        print("Enter a valid frequency")
"""
