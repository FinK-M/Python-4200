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


def csv_writer(prim, sec, ter):
    """
    ---------------------------------------------------------------------------
    FUNCTION: csv_writer
    INPUTS: values (str)
    RETURNS: prim, sec (list float)
    DEPENDENCIES: csv
    ---------------------------------------------------------------------------
    Takes two arrays of values and writes them to two columns in a csv file
    called "results.csv". The columns have headers "Input" and "Output"
    ---------------------------------------------------------------------------
    """
    rows = zip(ter, prim, sec)
    with open('results.csv', 'w', newline='') as csvfile:
        reswrite = csv.writer(csvfile)
        reswrite.writerow(["X1", "Y1", "Y2"])
        for row in rows:
            reswrite.writerow(row)


def dual_plot(x, x_label, y1, y1_label, y2, y2_label, x_min, x_max):
    fig, ax1 = plt.subplots()
    ax1.plot(x, y1, 'b')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.plot(x, y2, 'r')
    ax2.set_ylabel(y2_label, color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    plt.xlim([x_min, x_max])
    plt.grid(True)
    plt.show()

proceed = None
while not proceed:
    try:
        # create resource manager object
        rm = visa.ResourceManager()
    except:
        print("Error: Cannot find visa list, please check configuration")
        break

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
        break

    # display the intrument's reported ID. Note the commant 'ID' is
    # specific to the Keithley 4200-SCS. Others may use '*IDN?'
    print("Instrument IDs as", instr.query('ID'))

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
        break

    # print success
    print("Configured PMU2")

    # clear the buffer
    instr.write('BC')

    # read commands file into a list
    with open('commands_fsweep.txt', 'r') as f:
        commands = f.readlines()

    # parse list and send each item in turn to the instrument
    for command in commands:
        instr.write(command.rstrip('\n'))

    print("Running tests...")
    instr.wait_for_srq()
    print("Done!")

    instr.write(':CVU:DATA:Z?')
    values = str(instr.read_raw()).replace("b'", "").rstrip("'")
    values = values[:len(values) - 5]

    instr.write(':CVU:DATA:VOLT?')
    volt = str(instr.read_raw()).replace("b'", "").rstrip("'")
    volt = volt[:len(volt)-5].split(",")
    volts = [float(v) for v in volt]

    prim, sec = CV_output_san(values)

    prim = prim
    sec = sec
    volts = volts
    total = [prim[i]*sec[i] for i in range(len(prim))]

    csv_writer(prim, sec, volt)
    #plt.plot(volts, total)

    dual_plot(volts, "Voltage (V)", prim, "Capacitance (F)",
              sec, "Resistance", -5, 5)
    """
    print("Run again? (Y/N)")
    if str(input("Run again? (Y/N): ")) == "N" or "n":
        break
    """
    break
