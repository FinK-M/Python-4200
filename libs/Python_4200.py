import matplotlib.pyplot as plt
from math import log10, floor
from time import sleep
from IPython import display
import csv
import visa
from libs import cm110
from libs import ki4200
from libs import shutter


class cap_test(object):

    """
    ---------------------------------------------------------------------------
       _____              _____    _______   ______    _____   _______
      / ____|     /\     |  __ \  |__   __| |  ____|  / ____| |__   __|
     | |         /  \    | |__) |    | |    | |__    | (___      | |
     | |        / /\ \   |  ___/     | |    |  __|    \___ \     | |
     | |____   / ____ \  | |         | |    | |____   ____) |    | |
      \_____| /_/    \_\ |_|         |_|    |______| |_____/     |_|
    ---------------------------------------------------------------------------
    INHERITANCE: Object
    ---------------------------------------------------------------------------
    Contains general methods that can be used to set up any of the three types
    of capacitance tests. Is the parent class for the more specific CV, CF, and
    CT classes defined below
    ---------------------------------------------------------------------------
    """

    def __init__(self, label, mode, model, speed,
                 acv, length, dcvsoak, mono, shutter_port):
        self.mode = mode.lower()
        self.label = label
        self.model = model
        self.speed = speed
        self.acv = acv
        self.length = length
        self.dcvsoak = dcvsoak
        self.mono = mono
        self.shutter_port = shutter_port
        self.test_setup = False
        self.instrument_setup = False
        self.wrange_set = False
        self.single_w_val = 5500

    def set_name(self, label=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_name
        INPUTS: self, label(str)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if type(label) == str:
            self.label = label
        else:
            while True:
                try:
                    self.label = str(input("Enter test label: "))
                    break
                except:
                    print("Enter a valid label...")

    def set_mode(self, mode=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_mode
        INPUTS: self, mode(str)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        modes = ["cv", "cf", "ct"]
        if mode in modes:
            self.mode = mode.lower()
        else:
            while True:
                try:
                    response = str(input(
                        "Choose mode (cv, ct, or cf): ")).lower()
                    if response not in modes:
                        raise ValueError
                    else:
                        self.mode = response
                        break
                except ValueError:
                    print("Please choose a valid test mode...")

    def set_model(self, model=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_model
        INPUTS: self, model(str or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        models = ["z-theta", "r+jx", "cp-gp", "cs-rs", "cp-d", "cs-d"]
        try:
            if model in models:
                self.model = models.index(model)
            elif int(model) in range(6):
                self.model = int(model)
        except:
            while True:
                try:
                    print("Choose model",
                          "0: z-theta", "1: r+jx", "2: cp-gp",
                          "3: cs-rs", "4: cp-d", "5: cs-d")
                    response = input("Selection (0-5): ")
                    if response in models:
                        self.model = models.index(response)
                        break
                    elif int(response) in range(6):
                        self.model = int(response)
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter a valid selection")
        self.model

    def set_speed(self, speed=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_speed
        INPUTS: self, speed(int)
        RETURNS: none
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if speed in range(3):
            self.speed = speed
        elif speed == 4:
            pass
        else:
            while True:
                try:
                    response = int(input("Select integration speed: "))
                    if response in range(3):
                        self.speed = response
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter a correct value: ")

    def set_acv(self, acv=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_acv
        INPUTS: self, acv(int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if acv in range(10, 101):
            self.acv = acv/1000
        else:
            while True:
                try:
                    response = int(input("Enter ac ripple in millivolts: "))
                    if response in range(0, 101):
                        self.acv = response/1000
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter a valid voltage")

    def set_length(self, length=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_length
        INPUTS: self, length(str or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        lengths = ["0", "1.5", "3"]
        if str(length) in lengths:
            self.length = str(length)
        else:
            while True:
                try:
                    response = input("Enter cable length: ")
                    if response in lengths:
                        self.length = response
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid length")

    def set_dcvsoak(self, dcvsoak=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_dcvsoak
        INPUTS: self, dcvsoak(float or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if dcvsoak in range(-30, 30):
            self.dcvsoak = dcvsoak
        else:
            while True:
                try:
                    response = float(input("Enter DC Soak voltage: "))
                    if response in range(-30, 30):
                        self.dcvsoak = response
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid voltage")

    def set_delay(self, delay=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_delay
        INPUTS: self, delay(float or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if 0 < delay < 999:
            self.delay = delay
        else:
            while True:
                try:
                    delay = float(input("Enter delay time: "))
                    if 0 < delay < 999:
                        self.delay = delay
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid delay")

    def set_intrument(self):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_instrument
        INPUTS: self
        RETURNS: nothing
        DEPENDENCIES: pyvisa/visa
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if not self.instrument_setup:
            rm = visa.ResourceManager()
            self.instr = rm.open_resource("GPIB0::17::INSTR")
            ki4200.init_4200(1, self.instr)

        # self.instrument_setup = True

    def step_check(self, start, end, step):
        """
        ------------------------------------------------------------------------
        FUNCTION: step_check
        INPUTS: self, start, end, step (float or int)
        RETURNS: [start, end, step](float or int list)
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if step > abs(end - start):
            raise ValueError
        elif (end - start < 0 and step > 0) or (end - start > 0 and step < 0):
            step = - step
            return [start, end, step]
        else:
            return [start, end, step]

    def set_wavelengths(self, wstart=None, wend=None, wstep=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_wavelengths
        INPUTS: self, wstart, wend, wstep (int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if type(wstart) is int and type(wend) is int and type(wstep) is int:
            try:
                self.wstart, self.wend, self.wstep = self.step_check(
                    wstart, wend, wstep)
            except:
                print("Invalid variables entered")
        else:
            while True:
                try:
                    wstart = int(input("Enter start wavelength: "))
                    wend = int(input("Enter end wavelength: "))
                    wstep = int(input("Enter step size: "))
                    self.wstart, self.wend, self.wstep = self.step_check(
                        wstart, wend, wstep)
                    break
                except ValueError:
                    print("Please enter valid wavelengths...")
        self.wrange_set = True
        self.wsteps = 0
        for w in range(self.wstart, self.wend+1, self.wstep):
            self.wsteps += 1

    def set_single_w(self, w):
        self.single_w_val = w

    def set_shutter_port(self, p):
        self.shutter_port = p

    def set_mono_port(self, p):
        self.mono = p

    def set_second_delay(self, t):
        self.second_delay = t

    def set_minute_delay(self, t):
        self.minute_delay = t

    def set_second_wait(self, t):
        self.second_wait = t

    def set_minute_wait(self, t):
        self.minute_wait = t

    def set_open(self, o):
        self.open = str(int(o))

    def set_short(self, s):
        self.short = str(int(s))

    def set_load(self, l):
        self.load = str(int(l))

    def set_comp(self):
        return (self.open + "," + self.short + "," + self.load)

    def setup_test(self):
        """
        ------------------------------------------------------------------------
        FUNCTION: setup_test
        INPUTS: self
        RETURNS: nothing
        DEPENDENCIES: pyvisa/visa
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.commands = [":CVU:RESET",
                         ":CVU:MODE 1",
                         ":CVU:MODEL " + str(self.model),
                         ":CVU:SPEED " + str(self.speed),
                         ":CVU:ACV " + str(self.acv),
                         ":CVU:SOAK:DCV " + str(self.dcvsoak),
                         ":CVU:ACZ:RANGE " + str(self.acv),
                         ":CVU:CORRECT " + self.set_comp,
                         ":CVU:LENGTH " + str(self.length),
                         ":CVU:DELAY:SWEEP " + str(self.delay)]

        if self.mode == "cv":
            self.commands.append(":CVU:FREQ " + self.freq)
            self.commands.append(":CVU:SWEEP:DCV " + str(self.vstart) + ","
                                 + str(self.vend) + "," + str(self.vstep))
        elif self.mode == "cf":
            self.commands.append(":CVU:FREQ " + self.fstart + "," + self.fstop)

        self.set_intrument()
        for c in self.commands:
            self.instr.write(c)

    def run_test(self):
        """
        ------------------------------------------------------------------------
        FUNCTION: run_test
        INPUTS: self
        RETURNS: nothing
        DEPENDENCIES: pyvisa/visa, serial, time, pyplot
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.wait = self.second_wait + 60 * self.minute_wait
        self.delay = self.second_delay + 60 * self.minute_delay
        self.vsteps = floor(abs(self.vstart-self.vend)/abs(self.vstep))+1
        self.y = [[] for i in range(self.vsteps)]
        self.g = []

        self.setup_test()

        self.prim = []
        self.sec = []
        self.yaxis = []

        cm = cm110.setup_cm110(self.mono)
        sh = shutter.ard_shutter(port=self.shutter_port)

        if self.wrange_set:
            sh.open()
            i = 0
            self.wavelengths = []
            for w in range(self.wstart, self.wend+1, self.wstep):
                if self.wait > 0.5:
                    sh.close()
                cm110.command(cm, "goto", w)
                sleep(self.wait)
                if self.wait > 0.5:
                    sh.open()

                self.instr.write(":CVU:TEST:RUN")
                self.instr.wait_for_srq()

                self.instr.write(':CVU:DATA:Z?')
                values = (str(self.instr.read_raw())
                          .replace("b'", "").rstrip("'"))
                values = values[:-5]
                p, s = ki4200.CV_output_san(values)

                self.prim = p
                self.sec = s
                self.wavelengths.append(w)
                for j in range(len(self.prim)):
                    self.y[j].append(self.prim[j])
                    self.g.append(plt.plot(self.wavelengths, self.y[j], "b-"))
                display.display(plt.gcf())
                display.clear_output(wait=True)

                i += 1

            cm.close()
            sh.close()
            sh.shutdown()

            if self.mode == "cv":
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.instr)
            elif self.mode == "cf":
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.instr)
            self.instr.close()
            """
            for i in range(len(self.prim[0])):
                self.y = []
                for j in range(len(self.prim)):
                    self.y.append(self.prim[j][i])
            """

        else:
            cm110.command(cm, "goto", self.single_w_val)
            cm.close()
            sleep(1)
            sh.open()
            self.instr.write(":CVU:TEST:RUN")
            self.instr.wait_for_srq()

            self.instr.write(':CVU:DATA:Z?')
            values = (str(self.instr.read_raw())
                      .replace("b'", "").rstrip("'"))
            values = values[:-5]
            self.prim, self.sec = ki4200.CV_output_san(values)

            fig, ax = plt.subplots()
            if self.mode == "cv":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.instr)
                ax.plot(self.xaxis, self.prim)
                ax.set_xlabel("Volts (V)")
                ax.set_ylabel("Capacitance (F)")
            elif self.mode == "cf":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.instr)
                ax.plot(self.xaxis, self.prim)
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Capacitance (F)")
            self.instr.close()
            sh.close()
            sh.shutdown()

            display.display(fig)
            display.clear_output(wait=True)


class cv_test(cap_test):

    """
    ---------------------------------------------------------------------------
       _____  __      __  _______   ______    _____   _______
      / ____| \ \    / / |__   __| |  ____|  / ____| |__   __|
     | |       \ \  / /     | |    | |__    | (___      | |
     | |        \ \/ /      | |    |  __|    \___ \     | |
     | |____     \  /       | |    | |____   ____) |    | |
      \_____|     \/        |_|    |______| |_____/     |_|
    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------
    """

    def __init__(self, label, model=2, speed=1, acv=30,
                 length=1.5, dcvsoak=0, delay=0, mono="COM1",
                 shutter_port="COM12", wait=1, freq="1E+6"):
        self.label = label
        self.model = model
        self.speed = speed
        self.acv = acv/1000
        self.lenth = length
        self.dcvsoak = dcvsoak
        self.delay = delay
        self.mono = mono
        self.shutter_port = shutter_port
        self.wait = wait
        self.vrange_set = False
        self.freq = freq
        cap_test.__init__(self, label=label, mode="CV", model=model,
                          speed=speed, acv=acv/1000, length=length,
                          dcvsoak=dcvsoak, mono=mono,
                          shutter_port=shutter_port)

    def set_vrange(self, vstart=None, vend=None, vstep=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_vrange
        INPUTS: self, vstart, vend, vstep (float or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if not (vstart is None and vend is None and vstep is None):
            try:
                self.vstart, self.vend, self.vstep = self.step_check(
                    vstart, vend, vstep)
            except:
                print("Invalid variables entered")
        else:
            while True:
                try:
                    vstart = int(input("Enter start voltage: "))
                    vend = int(input("Enter end voltage: "))
                    vstep = float(input("Enter step size: "))
                    self.vstart, self.vend, self.vstep = self.step_check(
                        vstart, vend, vstep)
                    break
                except ValueError:
                    print("Please enter valid voltages...")
        self.vrange_set = True
        self.vsteps = floor((self.vstart-self.vend)/self.vstep)+1

    def set_freq(self, freq=None):

        frequencies = ['1K', '2K', '3K', '4K', '5K', '6K', '7K', '8K', '9K',
                       '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K',
                       '90K', '100K', '200K', '300K', '400K', '500K', '600K',
                       '700K', '800K', '900K', '1M', '2M', '3M', '4M', '5M',
                       '6M', '7M', '8M', '9M', '10M']

        if freq in frequencies:
            if "K" in freq:
                freq = int(freq[:-1])
                self.freq = '%.0E' % (freq*1000)
            else:
                freq = int(freq[:-1])
                self.freq = '%.0E' % (freq*1000000)
        else:
            print("Invalid frequency")


class cf_test(cap_test):

    """
    ---------------------------------------------------------------------------
       _____   ______   _______   ______    _____   _______
      / ____| |  ____| |__   __| |  ____|  / ____| |__   __|
     | |      | |__       | |    | |__    | (___      | |
     | |      |  __|      | |    |  __|    \___ \     | |
     | |____  | |         | |    | |____   ____) |    | |
      \_____| |_|         |_|    |______| |_____/     |_|
    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------
    """
    wrange_set = False
    vrange_set = False

    def __init__(self, label, model=3, speed=1, acv=30, length=1.5,
                 dcvsoak=0, delay=0, mono="COM1", wait=1):
        self.label = label
        self.model = model
        self.speed = speed
        self.acv = acv/1000
        self.lenth = length
        self.dcvsoak = dcvsoak
        self.delay = delay
        self.mono = mono
        self.wait = wait
        cap_test.__init__(self, label=label, mode="CF", model=model,
                          speed=speed, acv=acv/1000, length=length,
                          dcvsoak=dcvsoak, mono=mono)

    def sig_fig_1(self, x):
        if x in range(1000, 10000000, 1000):
            return round(x, -int(floor(log10(x))))
        else:
            raise ValueError("freq outside correct range")

    def set_frange(self, fstart=None, fend=None):
        try:
            self.fstart = self.sig_fig_1(fstart)
            self.fstop = self.sig_fig_1(fend)
        except:
            while True:
                try:
                    fstart = int(input("Enter start frequency: "))
                    fend = int(input("Enter end frequency: "))
                    self.fstart = self.sig_fig_1(fstart)
                    self.fend = self.sig_fig_1(fend)
                    break
                except ValueError:
                    print("Please enter valid frequencies...")

    def set_dcv(self, dcv=None):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_dcv
        INPUTS: self, dcv(float or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if dcv in range(-30, 30):
            self.dcv = dcv
        else:
            while True:
                try:
                    response = float(input("Enter DC voltage: "))
                    if response in range(-30, 30):
                        self.dcv = response
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid voltage")

"""
-------------------------------------------------------------------------------
  ______ _    _ _   _  _____ _______ _____ ____  _   _  _____
 |  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
 | |__  | |  | |  \| | |       | |    | || |  | |  \| | (___
 |  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \
 | |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
 |_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/
-------------------------------------------------------------------------------
"""


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


# If running this library, print doc string for all functions
if __name__ == "__main__":
    print("library imported")
