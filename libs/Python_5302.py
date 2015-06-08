import visa
from time import sleep


if __name__ == "__main__":
    try:
        # create resource manager object
        rm = visa.ResourceManager()
    except:
        print("Error: Cannot find visa list, please check configuration")
        exit()

    # pass resource manager to device selection prompt
    # comment to set device without prompt
    # addr = select_device(rm)

    # addr = 'GPIB0::17::INSTR'
    # uncomment to set device without prompt

    # confirm address being used
    # print("Using device at", addr)

    # open visa resource at given address
    try:
        instr = rm.open_resource("GPIB0::12::INSTR")
        instr.query_delay = 0.05
    except:
        print("Error, cannot open resource")
        exit()

    """
    display the intrument's reported ID. Note the commant 'ID' is
    specific to 5302 LIA. Others may use '*IDN?'.
    """
    print(instr.query('ID'))
    while True:

        freq = str(int(instr.query('FRQ'))/1000)
        mag = str(int(instr.query('MAG'))/100)
        pha = str(int(instr.query('PHA'))/1000)
        print(freq + " Hz  " + mag + " %  " + pha)
        sleep(.5)
