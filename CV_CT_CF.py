from libs.Python_4200 import *
import time
from os import path

class instrument(object):
    """docstring for instrument"""
    def __init__(self, arg):
        super(instrument, self).__init__()
        self.arg = arg
        

if __name__ == "__main__":

    try:
        # create resource manager object
        rm = visa.ResourceManager()
    except:
        raise RuntimeError("Cannot find visa list, please check configuration")

    # pass resource manager to device selection prompt
    # comment to set device without prompt
    addr = select_device(rm)

    # confirm address being used
    print("Using device at", addr)

    # open visa resource at given address
    try:
        instr = rm.open_resource(addr)
    except:
        print("Error, cannot open resource")
        raise SystemExit()

    # display the intrument's reported ID. Note the commant 'ID' is
    # specific to the Keithley 4200-SCS. Others may use '*IDN?'
    print("Instrument IDs as", instr.query('ID'))

    init_4200(1, instr)

    while True:
        ttype = test_type()
        script_dir = path.dirname(__file__) #<-- absolute dir the script is in
        if ttype == 0:
            rel_path = "data/commands_vsweep.txt"
            cfile = path.join(script_dir, rel_path)
        elif ttype == 1:
            rel_path = "data/commands_fsweep.txt"
            cfile = path.join(script_dir, rel_path)
        elif ttype == 2:
            rel_path = "data/commands_tsweep.txt"
            cfile = path.join(script_dir, rel_path)

        # read commands file into a list
        try:
            with open(cfile, 'r') as coms:
                commands = coms.readlines()
                coms.close()
        except:
            raise SystemExit('Could not open command file!')

        # parse list and send each item in turn to the instrument
        for c in commands:
            instr.write(c.rstrip('\n'))

        print("Running tests...")
        instr.wait_for_srq(timeout=5000)
        print("Done!")

        instr.write(':CVU:DATA:Z?')
        values = str(instr.read_raw()).replace("b'", "").rstrip("'")
        values = values[:-5]
        prim, sec = CV_output_san(values)

        if ttype == 0:
            volt = read_4200_x(':CVU:DATA:VOLT?', instr)
            csv_writer(prim, sec, volt, str(int(time.time())) + '_CV')
            dual_plot(volt, "Volts (V)", prim, "Capacitance (F)",
                      sec, "Resistance (Ω)", min(volt), max(volt), False)

        elif ttype == 1:
            freq = read_4200_x(':CVU:DATA:FREQ?', instr)
            csv_writer(prim, sec, freq, str(int(time.time())) + '_CF')
            dual_plot(freq, "Frequency (Hz)", prim, "Capacitance (F)",
                      sec, "Resistance (Ω)", min(freq), max(freq), True)

        elif ttype == 2:
            tstamp = read_4200_x(':CVU:DATA:TSTAMP?', instr)
            csv_writer(prim, sec, tstamp, str(int(time.time())) + '_CT')
            dual_plot(tstamp, "Time (S)", prim, "Capacitance (F)",
                      sec, "Resistance (Ω)", min(tstamp), max(tstamp), False)

        check = True
        while check:
            try:
                c = str(input("Run again? (Y/N): ")).lower()
                if c == "n":
                    raise SystemExit(0)
                elif c == "y":
                    print()
                    check = False
                else:
                    raise ValueError()
            except ValueError:
                print("Please make a valid selection")
