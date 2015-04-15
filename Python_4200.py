import matplotlib.pyplot as plt
from decimal import Decimal
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
    prim = [float(Decimal(values[i])) for i in range(0, len(values), 2)]
    sec = [float(values[i]) for i in range(1, len(values), 2)]
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
            name (str)
    RETURNS: nothing
    DEPENDENCIES: csv
    ---------------------------------------------------------------------------
    Takes three arrays of values and writes them to two columns in a csv file
    called "name". The columns have headers "X1", "Y1", and "Y2"
    ---------------------------------------------------------------------------
    """
    rows = zip(ter, prim, sec)
    try:
        with open(name + '.csv', 'w', newline='') as csvfile:
            reswrite = csv.writer(csvfile)
            reswrite.writerow(["X1", "Y1", "Y2"])
            for row in rows:
                reswrite.writerow(row)
    except:
        raise SystemExit("Could not open file to write!")


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
    print("Test 0: CV sweep\n",
          "Test 1: CF sweep\n",
          "Test 2: CT sweep")

    while True:
        try:
            t_type = int(input("Please select a test: "))
            if t_type != 0 and t_type != 1 and t_type != 2:
                raise ValueError("Please enter 2, 1, or 0")
            else:
                return t_type
        except ValueError:
            print("Invalid selection")


def read_4200_x(read_command, instrument):
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

    instrument.write(read_command)
    data = str(instrument.read_raw()).replace("b'", "").rstrip("'")
    data = data[:-5].split(",")
    x = [float(d) for d in data]
    return x

def rpm_switch(channel, mode, instrument):
    """
    ---------------------------------------------------------------------------
    FUNCTION: rpm_switch
    INPUTS: channel, mode (int)
    RETURNS: nothing
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Sends a command to the 4225 RPM modules of the 4200-SCS to set a given
    channel to a given mode (see below).
    0 = Pulsing
    1 = 2 Wire CVU
    2 = 4 Wire CVU
    3 = SMU
    ---------------------------------------------------------------------------
    """
    try:
        # run script to switch RPM1 to CVU mode
        instrument.write('EX pmuulib kxci_rpm_switch(' + str(channel) + ',' + str(mode) + ')')
        # wait for script to complete
        instrument.wait_for_srq()
        print("Configured PMU", channel)
    except:
        raise RuntimeError("Service Request timed out")

def init_4200(mode, instrument):
    """
    ---------------------------------------------------------------------------
    FUNCTION: init_4200
    INPUTS: mode, instrument (int)
    RETURNS: nothing
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Sets up the 4200-SCS to recieve measurement commands and respond correctly
    when RPM modules are attached. See function above for RPM modes.
    ---------------------------------------------------------------------------
    """
    # clear the visa resource buffers
    instrument.clear()
    # send srq when finished with task
    instrument.write('DR1')
    # access the user library page
    instrument.write('UL')
    rpm_switch(1, mode, instrument)
    rpm_switch(2, mode, instrument)
    # clear the buffer
    instrument.write('BC')


# If running this library, print docstring for all functions
if __name__ == "__main__":
    
    print(CV_output_san.__doc__, '\n',
          select_device.__doc__, '\n',
          csv_writer.__doc__,    '\n',
          dual_plot.__doc__,     '\n',
          test_type.__doc__,     '\n',
          read_4200_x.__doc__,   '\n',
          rpm_switch.__doc__,    '\n',
          init_4200.__doc__,     '\n')
