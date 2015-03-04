from Python_4200 import *

if __name__ == "__main__":

    try:
        # create resource manager object
        rm = visa.ResourceManager()
    except:
        raise RuntimeError("Cannot find visa list, please check configuration")

    # pass resource manager to device selection prompt
    # comment to set device without prompt
    addr = select_device(rm)

    # addr = 'GPIB0::17::INSTR'
    # uncomment to set device without prompt

    # confirm address being used
    print("Using device at", addr)

    # open visa resource at given address
    try:
        instr = rm.open_resource(addr)
    except:
        print("Error, cannot open resource")
        exit()

    # display the intrument's reported ID. Note the commant 'ID' is
    # specific to the Keithley 4200-SCS. Others may use '*IDN?'
    print("Instrument IDs as", instr.query('ID'))

    while True:
        ttype = test_type()

        # clear the visa resource buffers
        instr.clear()

        # send srq when finished with task
        instr.write('DR1')
        # access the user library page
        instr.write('UL')
        # run script to switch RPM1 to CVU mode
        instr.write('EX pmuulib kxci_rpm_switch(1,1)')
        # wait for script to complete
        instr.wait_for_srq()
        # print success
        print("Configured PMU1")

        # run script to switch RPM2 to CVU mode
        instr.write('EX pmuulib kxci_rpm_switch(2,1)')
        # wait for script to complete
        try:
            instr.wait_for_srq()
        except:
            raise RuntimeError("Service Request timed out")

        # print success
        print("Configured PMU2")

        # clear the buffer
        instr.write('BC')

        if ttype == 0:
            cfile = 'commands_vsweep.txt'
        elif ttype == 1:
            cfile = 'commands_fsweep.txt'
        elif ttype == 2:
            cfile = 'commands_tsweep.txt'
        # read commands file into a list
        with open(cfile, 'r') as coms:
            commands = coms.readlines()
            coms.close()

        # parse list and send each item in turn to the instrument
        for command in commands:
            instr.write(command.rstrip('\n'))

        print("Running tests...")
        instr.wait_for_srq(timeout=250000)
        print("Done!")

        instr.write(':CVU:DATA:Z?')
        values = str(instr.read_raw()).replace("b'", "").rstrip("'")
        values = values[:-5]
        prim, sec = CV_output_san(values)

        if ttype == 0:
            volt = read_4200_x(':CVU:DATA:VOLT?')
            csv_writer(prim, sec, volt, 'CV_results.csv')
            dual_plot(volt, "Volts (V)", prim, "Capacitance (F)",
                      sec, "Resistance (Ω)", min(volt), max(volt), False)

        elif ttype == 1:
            freq = read_4200_x(':CVU:DATA:FREQ?')
            csv_writer(prim, sec, freq, 'CF_results.csv')
            dual_plot(freq, "Frequency (Hz)", prim, "Capacitance (F)",
                      sec, "Resistance (Ω)", min(freq), max(freq), True)

        elif ttype == 2:
            tstamp = read_4200_x(':CVU:DATA:TSTAMP?')
            csv_writer(prim, sec, tstamp, 'CT_results.csv')
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