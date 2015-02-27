import matplotlib.pyplot as plt
from decimal import *
import visa
import csv
import time


def CV_output_san(values):
    """
    ---------------------------------------------------------------------------
    FUNCTION: CV_output_san
    INPUTS: values (str)
    RETURNS: prim, sec (list float)
    DEPENDENCIES: none
    ---------------------------------------------------------------------------
    Takes data string as proudced by KXCI command :CVU:OUTPUT:Z? and returns
    two arrays of decimal numbers representing the pairs of values receieved
    ---------------------------------------------------------------------------
    """
    values = (values.replace(";", ",").split(","))
    prim = [values[i] for i in range(0, len(values), 2)]
    sec = [float(values[i]) for i in range(1, len(values), 2)]
    prim = [float(Decimal(prim[i])) for i in range(len(prim))]
    return prim, sec


def select_device(rm):
    """
    ---------------------------------------------------------------------------
    FUNCTION: select_device
    INPUTS: rm (visa.ResourceManager)
    RETURNS: devices[selection] (str)
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Takes a resource manager as an argument and lists available visa devices
    The user is then queried as to which device they would like to open
    ---------------------------------------------------------------------------
    """
    devices = rm.list_resources()

    print("Found the following ", len(devices), " devices")
    for i in range(len(devices)):
        print(i, ") ", devices[i])

    selection = None
    while not selection:
        try:
            selection = int(input("Please select device address: "))
        except ValueError:
            print("Invalid Number")

    return(devices[selection])


def csv_writer(prim, sec, ter, name):
    """
    ---------------------------------------------------------------------------
    FUNCTION: csv_writer
    INPUTS: prim, sec, ter (float list)
    RETURNS: nothing
    DEPENDENCIES: csv
    ---------------------------------------------------------------------------
    Takes three arrays of values and writes them to two columns in a csv file
    called "results.csv". The columns have headers "X1", "Y1", and "Y2"
    ---------------------------------------------------------------------------
    """
    rows = zip(ter, prim, sec)
    with open(name, 'w', newline='') as csvfile:
        reswrite = csv.writer(csvfile)
        reswrite.writerow(["X1", "Y1", "Y2"])
        for row in rows:
            reswrite.writerow(row)


def dual_plot(x, x_label, y1, y1_label, y2, y2_label, x_min, x_max, log):
    """
    ---------------------------------------------------------------------------
    FUNCTION: dual_plot
    INPUTS: x, y1, y2 (float array)
            x_min, x_max (int)
            x_label, y1_label, y2_label (str)
            log (bool)
    RETURNS: nothing
    DEPENDENCIES: matplotlib.pyplot
    ---------------------------------------------------------------------------
    Takes three arrays of floats and their respective names. y1 and y2 are
    plotted against x over the range x_min to x_max. Setting log to true
    results in a semilogx plot whereas false is a simple linear plot.
    ---------------------------------------------------------------------------
    """
    fig, ax1 = plt.subplots()

    if log:
        ax1.semilogx(x, y1, 'b')
    else:
        ax1.plot(x, y1, 'b')

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color='b')

    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()

    if log:
        ax2.semilogx(x, y2, 'r')
    else:
        ax2.plot(x, y2, 'r')
    ax2.set_ylabel(y2_label, color='r')

    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    plt.xlim([x_min, x_max])
    plt.grid(True)
    plt.show(block=False)


def test_type():
    """
    ---------------------------------------------------------------------------
    FUNCTION: test_type
    INPUTS: none
    RETURNS: t_type (int)
    DEPENDENCIES: none
    ---------------------------------------------------------------------------
    Queries the user on which test they wish to perform, selecting an incorrect
    value results in an error message and a prompt to choose again.
    ---------------------------------------------------------------------------
    """
    print("Test 0: CV sweep")
    print("Test 1: CF sweep")
    print("Test 2: CT sweep")

    while True:
        try:
            t_type = int(input("Please select a test: "))
            if t_type != 0 and t_type != 1 and t_type != 2:
                raise ValueError("Please enter 2, 1, or 0")
            else:
                return t_type
        except ValueError:
            print("Invalid selection")


def read_4200_x(read_command):
    """
    ---------------------------------------------------------------------------
    FUNCTION: read_4200_x
    INPUTS: read_command (str)
    RETURNS: x (float list)
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Takes an appropriate CVU read command as an argument and sends it to a
    4200-SCS. Then reads the raw returned data and formats it into an list of
    floats. Acceptable read commands are:
    :CVU:DATA:VOLT?
    :CVU:DATA:FREQ?
    :CVU:DATA:STATUS?
    :CVU:DATA:TSTAMP?
    ---------------------------------------------------------------------------
    """
    ok_commands = [':CVU:DATA:VOLT?', ':CVU:DATA:FREQ?',
                   ':CVU:DATA:STATUS?', ':CVU:DATA:TSTAMP?']
    if read_command not in ok_commands:
        raise ValueError('Incorrect read command passed')

    instr.write(read_command)
    data = str(instr.read_raw()).replace("b'", "").rstrip("'")
    data = data[:-5].split(",")
    x = [float(d) for d in data]
    return x


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
