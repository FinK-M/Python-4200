import matplotlib.pyplot as plt
from decimal import *
import visa
import csv


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
    INPUTS: x, y1, y2 (float array) - x_min, x_max (int)
            x_label, y1_label, y2_label (str) - log (Boolean)
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


try:
    # create resource manager object
    rm = visa.ResourceManager()
except:
    print("Error: Cannot find visa list, please check configuration")
    exit()

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
        print("Error: SRQ timeout")
        exit()

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
    values = values[:len(values) - 5]
    prim, sec = CV_output_san(values)

    if ttype == 0:
        instr.write(':CVU:DATA:VOLT?')
        volt = str(instr.read_raw()).replace("b'", "").rstrip("'")
        volt = volt[:len(volt)-5].split(",")
        volts = [float(v) for v in volt]
        csv_writer(prim, sec, volts, 'CV_results.csv')
        dual_plot(volts, "Volts (V)", prim, "Capacitance (F)",
                  sec, "Resistance", -5, 5, False)
    elif ttype == 1:
        instr.write(':CVU:DATA:FREQ?')
        freq = str(instr.read_raw()).replace("b'", "").rstrip("'")
        freq = freq[:len(freq)-5].split(",")
        freqs = [float(f) for f in freq]
        csv_writer(prim, sec, freqs, 'CF_results.csv')
        dual_plot(freqs, "Frequency (Hz)", prim, "Capacitance (F)",
                  sec, "Resistance", 1000, 1000000, True)

    elif ttype == 2:
        instr.write(':CVU:DATA:TSTAMP?')
        ta = str(instr.read_raw()).replace("b'", "").rstrip("'")
        ta = ta[:len(ta)-5].split(",")
        tb = [float(t) for t in ta]
        csv_writer(prim, sec, tb, 'CT_results.csv')
        dual_plot(tb, "Time (S)", prim, "Capacitance (F)",
                  sec, "Resistance", 0, 13, False)

    check = True
    while check:
        try:
            c = str(input("Run again? (Y/N): ")).lower()
            if c == "n":
                raise SystemExit(0)
            elif c == "y":
                check = False
            else:
                raise ValueError()
        except ValueError:
            print("Please make a valid selection")
