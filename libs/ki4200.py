from decimal import Decimal


def CV_output_san(values):
    """
    ---------------------------------------------------------------------------
    FUNCTION: CV_output_san
    INPUTS: values (str)
    RETURNS: prim, sec (list float)
    DEPENDENCIES: none
    ---------------------------------------------------------------------------
    Takes data string as produced by KXCI command :CVU:OUTPUT:Z? and returns
    two arrays of decimal numbers representing the pairs of values received
    ---------------------------------------------------------------------------
    """
    values = values.replace(";", ",").split(",")
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


def read_4200_x(read_command, instrument):
    """
    ---------------------------------------------------------------------------
    FUNCTION: read_4200_x
    INPUTS: read_command (str), instrument (visa resource)
    RETURNS: x (float list)
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Takes an appropriate CVU read command as an argument and sends it to a
    4200-SCS. Then reads the raw returned data and formats it into an list of
    floats. Acceptable read commands are:
    1) volt --> :CVU:DATA:VOLT?
    2) freq --> :CVU:DATA:FREQ?
    3) status --> :CVU:DATA:STATUS?
    4) time --> :CVU:DATA:TSTAMP?
    ---------------------------------------------------------------------------
    """
    commands = {"volts": ":CVU:DATA:VOLT?",
                "freq": ":CVU:DATA:FREQ?",
                "status": ":CVU:DATA:STATUS?",
                "time": ":CVU:DATA:TSTAMP?"}
    try:
        assert(read_command in commands.keys())
    except AssertionError:
        print('Incorrect read command passed')

    instrument.write(commands[read_command])
    data = instrument.read(termination=",\r\n", encoding="utf-8").split(",")
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
    running = True
    count = 0
    while running and count <= 3:
        try:
            # run script to switch RPM1 to CVU mode
            instrument.write('EX pmuulib kxci_rpm_switch('
                             + str(channel) + ',' + str(mode) + ')')
            # wait for script to complete
            instrument.wait_for_srq(timeout=3000)
            # print("Configured PMU", channel)
            running = False
        except:
            print("Service Request timed out")
            count += 1


def init_4200(rpm, mode, instrument):
    """
    ---------------------------------------------------------------------------
    FUNCTION: init_4200
    INPUTS: rpm (bool), mode, instrument (int)
    RETURNS: nothing
    DEPENDENCIES: pyvisa/visa
    ---------------------------------------------------------------------------
    Sets up the 4200-SCS to receive measurement commands and respond correctly
    when RPM modules are attached. See function above for RPM modes.
    ---------------------------------------------------------------------------
    """
    # clear the visa resource
    instrument.clear()
    # send srq when finished with task
    instrument.write('DR1')
    if rpm:
        # access the user library page
        instrument.write('UL')
        rpm_switch(1, mode, instrument)
        rpm_switch(2, mode, instrument)
    # clear the buffer
    instrument.write('BC')
