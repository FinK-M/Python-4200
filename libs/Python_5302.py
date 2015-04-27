import visa
from time import sleep
from Python_4200 import select_device


def query_5302(query):
    """
    Simple query routine that adds short delay to allow
    5302 LIA to respond to writen string.
    """
    instr.write(query)
    sleep(0.05)
    return instr.read()

if __name__ == "__main__":
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
