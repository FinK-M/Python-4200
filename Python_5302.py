import visa
from time import sleep


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


def query_5302(query):
    """
    Simple query routine that adds short delay to allow
    5302 LIA to respond to writen string.
    """
    instr.write(query)
    sleep(0.01)
    return instr.read()


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

"""
display the intrument's reported ID. Note the commant 'ID' is
specific to 5302 LIA. Others may use '*IDN?'.
"""
print(query_5302('ID'))
print(int(query_5302('FRQ'))/1000, 'KHz')
print(query_5302('VER'))
sleep(5)
