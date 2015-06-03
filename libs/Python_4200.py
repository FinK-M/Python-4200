import matplotlib.pyplot as plt
from math import log10, floor
from time import sleep
from IPython import display
import csv
import visa
from libs import cm110
from libs import ki4200
from libs import shutter
import os
from datetime import datetime
import re


class K4200_test(object):

    """
    ---------------------------------------------------------------------------
     _  __  _  _     ___     ___     ___    _______   ______    _____   _______
    | |/ / | || |   |__ \   / _ \   / _ \  |__   __| |  ____|  / ____| |__   __
    | ' /  | || |_     ) | | | | | | | | |    | |    | |__    | (___      | |
    |  <   |__   _|   / /  | | | | | | | |    | |    |  __|    \___ \     | |
    | . \     | |    / /_  | |_| | | |_| |    | |    | |____   ____) |    | |
    |_|\_\    |_|   |____|  \___/   \___/     |_|    |______| |_____/     |_|
    ---------------------------------------------------------------------------
    INHERITANCE: Object
    ---------------------------------------------------------------------------
    Contains general methods that can be used to set up any of the three types
    of capacitance tests. Is the parent class for the more specific CV, CF, and
    CT classes defined below
    ---------------------------------------------------------------------------
    """
    rm = visa.ResourceManager()
    ls331_address = "GPIB0::1::INSTR"
    k4200_address = "GPIB0::17::INSTR"
    mono_port = ""
    shutter_port = ""
    cust_name = ""
    run_all = False

    def __init__(self, label, speed, delay, mono_port, shutter_port, mode):
        self.label = label
        self.speed = speed
        self.delay = delay
        self.mode = mode

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

    def set_delay(self, delay):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_delay
        INPUTS: self, delay(float or int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if 0 <= delay <= 60:
            self.delay = delay
        else:
            while True:
                try:
                    delay = float(input("Enter delay time: "))
                    if 0 < delay <= 60:
                        self.delay = delay
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid delay")

    def set_wait(self, wait_sec, wait_min):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_wait
        INPUTS: self, wait_sec, wait_min(int)
        RETURNS: nothing
        DEPENDENCIES: none
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        wait = wait_sec + wait_min * 60
        if 0 <= wait <= 3660:
            self.wait = wait
        else:
            while True:
                try:
                    wait = float(input("Enter wait time: "))
                    if 0 < wait <= 3660:
                        self.wait = wait
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Please enter valid wait time")

    def set_address(self, instrument, address):
        if instrument == "K4200":
            self.k4200_address = address
        elif instrument == "LS331":
            self.ls331_address = address

    def set_visa_instr(self, instrument):
        """
        ------------------------------------------------------------------------
        FUNCTION: set_visa_instr
        INPUTS: self
        RETURNS: nothing
        DEPENDENCIES: pyvisa/visa
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        if instrument == "K4200":
            self.k4200 = self.rm.open_resource(self.k4200_address)
            ki4200.init_4200(1, self.k4200)
        elif instrument == "LS331":
            self.ls331 = self.rm.open_resource(self.ls331_address)

    def set_shutter_port(self, p):
        self.shutter_port = p

    def set_mono_port(self, p):
        self.mono_port = p

    def set_custom_name(self, name):
        if name == "":
            self.cust_name = ""
        else:
            self.cust_name = (re.sub('[\/:*?"<>| ]', '',
                                     "_" + str(name)).rstrip())


class cap_test(K4200_test):

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
    length = "1.5"

    def __init__(self, label, mode, model, speed, delay,
                 acv, length, dcvsoak, mono_port, shutter_port):
        self.model = model
        self.acv = acv
        self.acz = "0"
        self.comps = "0,0,0"
        self.length = length
        self.dcvsoak = dcvsoak
        self.wrange_set = False
        self.single_w_val = 5500
        K4200_test.__init__(self, label=label, speed=speed, delay=delay,
                            mono_port=mono_port, shutter_port=shutter_port,
                            mode=mode)

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

    def set_acz(self, acz):
        self.acz = acz

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

    def set_comps(self, open, short, load):
        self.comps = (str(int(open)) + "," + str(int(short)) +
                      "," + str(int(load)))

    def save_to_csv(self, date, time, xdata, ydata, zdata=None):

        if self.mode == "cv":
            if self.wrange_set:
                header = ["wavelength"]
                for v in self.yaxis:
                    header.append(str(v) + "V")
                header.append("Temperature (K)")
                for i in range(len(ydata)):
                    ydata[i].insert(0, xdata[i])
                    ydata[i].append(zdata[i])
                data = ydata

            else:
                header = ["Voltage", "Capacitance"]
                data = ([[xdata[i], ydata[i]] for i in range(len(xdata))])

        if self.mode == 'cf':
            if self.wrange_set:
                header = ["wavelength"]
                for f in self.yaxis:
                    header.append(str(f) + "Hz")
                header.append("Temperature (K)")
                for i in range(len(ydata)):
                    ydata[i].insert(0, xdata[i])
                    ydata[i].append(zdata[i])
                data = ydata
            else:
                header = ["Frequency", "Capacitance"]
                data = [[xdata[i], ydata[i]] for i in range(len(xdata))]

        self.folder = os.path.join(os.getcwd(), "data/" + date)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.filename = time + "_" + self.mode + "_"
        if self.wrange_set:
            self.filename += "multi" + self.cust_name + ".csv"
        else:
            self.filename += "single" + self.cust_name + ".csv"
        self.final_path = os.path.join(self.folder, self.filename)
        with open(self.final_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(data)
            csvfile.close()

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
        plt.clf()
        plt.close()
        plt.figure(
            num=1,
            figsize=(14, 5),
            dpi=80,
            facecolor='w',
            edgecolor='k')

        ax2 = None
        if self.wrange_set:
            ax1 = plt.subplot(121)
            ax1.minorticks_on()
            ax1.grid(b=True, which='major', color='#6C7A89')
            ax1.grid(b=True, which='minor', color='#D2D7D3')
            if self.mode == "cv":
                ax1.set_title(
                    "CVW sweep",
                    fontsize=20,
                    family="serif")
            elif self.mode == "cf":
                ax1.set_title(
                    "CFW sweep",
                    fontsize=20,
                    family="serif")
            ax1.set_xlabel("Wavelength (Angstoms)", fontsize=14)
            ax1.set_ylabel("Capacitance (F)", fontsize=14)

            ax2 = plt.subplot(122)
            ax2.minorticks_on()
            ax2.grid(b=True, which='major', color='#6C7A89')
            ax2.grid(b=True, which='minor', color='#D2D7D3')
            ax2.set_title(
                "Temperature",
                fontsize=20,
                family="serif")
            ax2.set_xlabel("Wavelength (Angstoms)", fontsize=14)
            ax2.set_ylabel("Temperature (C)", fontsize=14)
            ax1.plot()
            ax2.plot()
            plt.tight_layout(h_pad=1.0)
        elif self.mode == "cv":
            ax1 = plt.subplot(111)
            ax1.minorticks_on()
            ax1.grid(b=True, which='major', color='#6C7A89')
            ax1.grid(b=True, which='minor', color='#D2D7D3')
            ax1.set_title(
                "CV sweep at " + str(self.single_w_val/10) + "nm",
                fontsize=20,
                family="serif")
            ax1.set_xlabel("Volts (V)", fontsize=14)
            ax1.set_ylabel("Capacitance (F)", fontsize=14)
            ax1.plot()
        elif self.mode == "cf":
            ax1 = plt.subplot(111)
            ax1.minorticks_on()
            ax1.grid(b=True, which='major', color='#6C7A89')
            ax1.grid(b=True, which='minor', color='#D2D7D3')
            ax1.set_title(
                "CF sweep at " + str(self.single_w_val/10) + "nm",
                fontsize=20,
                family="serif")
            ax1.set_xlabel("Frequency (Hz)", fontsize=14)
            ax1.set_ylabel("Capacitance (F)", fontsize=14)
            ax1.semilogx()

        display.display(plt.gcf())
        display.clear_output(wait=True)

        self.commands = [":CVU:RESET",
                         ":CVU:MODE 1",
                         ":CVU:MODEL " + str(self.model),
                         ":CVU:SPEED " + str(self.speed),
                         ":CVU:ACV " + str(self.acv),
                         ":CVU:SOAK:DCV " + str(self.dcvsoak),
                         ":CVU:ACZ:RANGE " + self.acz,
                         ":CVU:CORRECT " + self.comps,
                         ":CVU:LENGTH " + str(self.length),
                         ":CVU:DELAY:SWEEP " + str(self.delay)]

        if self.mode == "cv":
            self.commands.append(":CVU:FREQ " + self.freq)
            self.commands.append(":CVU:SWEEP:DCV " + str(self.vstart) + ","
                                 + str(self.vend) + "," + str(self.vstep))
        elif self.mode == "cf":
            self.commands.append(
                ":CVU:SWEEP:FREQ " + self.fstart + "," + self.fstop)

        self.set_visa_instr(instrument="K4200")
        for c in self.commands:
            self.k4200.write(c)
        self.set_visa_instr(instrument="LS331")

        cm = cm110.setup_cm110(self.mono_port)
        sh = shutter.ard_shutter(port=self.shutter_port)
        return ax1, ax2, cm, sh

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
        colours = ["g", "b", "r", "c", "m", "y", "k"]
        display.clear_output(wait=True)
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H.%M.%S")

        ax1, ax2, cm, sh = self.setup_test()
        self.prim = []
        self.sec = []
        self.yaxis = []
        self.temp = []

        if self.wrange_set:

            sh.open()
            self.wavelengths = []
            for w in range(self.wstart, self.wend+1, self.wstep):
                self.temp.append(
                    float(self.ls331.query('CRDG?').replace('+', '')))

                if self.wait > 0.5:
                    sh.close()
                cm110.command(cm, "goto", w)
                sleep(self.wait)
                if self.wait > 0.5:
                    sh.open()

                self.k4200.write(":CVU:TEST:RUN")
                self.k4200.wait_for_srq()
                self.k4200.write(':CVU:DATA:Z?')
                values = self.k4200.read(termination=",\r\n", encoding="utf-8")
                p, s = ki4200.CV_output_san(values)

                self.prim.append(p)
                self.sec.append(s)
                self.wavelengths.append(w)

                self.y = (list(map(list, zip(*self.prim))))
                i = 0
                for line in self.y:
                    if w > self.wstart:
                        del(ax1.lines[-len(self.y)])
                        del(ax2.lines[-1])
                    if i < 7:
                        ax1.plot(self.wavelengths, line, colours[i])
                    else:
                        ax1.plot(self.wavelengths, line)
                    ax2.plot(self.wavelengths, self.temp, 'b-')
                    display.display(plt.gcf())
                    display.clear_output(wait=True)
                    i += 1

            cm.close()
            sh.close()
            sh.shutdown()

            if self.mode == "cv":
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.k4200)
            elif self.mode == "cf":
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.k4200)
            self.k4200.close()

            self.save_to_csv(
                date=date,
                time=time,
                xdata=self.wavelengths,
                ydata=self.prim,
                zdata=self.temp)
            imgname = ("data/" + date + "/" + time + "_" + self.mode + "_" +
                       "multi" + self.cust_name + ".png")
            plt.savefig(imgname)
            return 0

        else:
            cm110.command(cm, "goto", self.single_w_val)
            cm.close()
            sleep(1)
            sh.open()
            self.k4200.write(":CVU:TEST:RUN")
            self.k4200.wait_for_srq()

            self.k4200.write(':CVU:DATA:Z?')
            values = (str(self.k4200.read_raw())
                      .replace("b'", "").rstrip("'"))
            values = values[:-5]
            self.prim, self.sec = ki4200.CV_output_san(values)

            if self.mode == "cv":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.k4200)
                ax1.plot(self.xaxis, self.prim)
            elif self.mode == "cf":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.k4200)
                ax1.plot(self.xaxis, self.prim)
            self.k4200.close()
            sh.close()
            sh.shutdown()

            self.save_to_csv(
                date=date,
                time=time,
                xdata=self.xaxis,
                ydata=self.prim)

            display.display(plt.gcf())
            display.clear_output(wait=True)
            return 0


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
                 length=1.5, dcvsoak=0, delay=0, mono_port="COM1",
                 shutter_port="COM12", wait=1, freq="1E+6"):
        self.label = label
        self.model = model
        self.speed = speed
        self.acv = acv/1000
        self.lenth = length
        self.dcvsoak = dcvsoak
        self.delay = delay
        self.wait = wait
        self.vrange_set = False
        self.freq = freq
        cap_test.__init__(self, label=label, mode="cv", model=model,
                          speed=speed, acv=acv/1000, length=length,
                          dcvsoak=dcvsoak, mono_port=mono_port,
                          shutter_port=shutter_port, delay=delay)

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

    def set_freq(self, f_num, f_order):
        freq = int(f_num) * f_order
        self.freq = '%.0E' % freq


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
                 dcvsoak=0, delay=0, mono_port="COM1", wait=1,
                 shutter_port="COM12", fstart="1E+6", fstop="3E+6"):
        self.label = label
        self.model = model
        self.speed = speed
        self.acv = acv/1000
        self.lenth = length
        self.dcvsoak = dcvsoak
        self.delay = delay
        self.mono_port = mono_port
        self.wait = wait
        self.fstart = fstart
        self.fstop = fstop
        cap_test.__init__(self, label=label, mode="cf", model=model,
                          speed=speed, acv=acv/1000, length=length,
                          dcvsoak=dcvsoak, mono_port=mono_port,
                          shutter_port=shutter_port, delay=delay)

    def sig_fig_1(self, x):
        if x in range(1000, 10000000, 1000):
            return round(x, -int(floor(log10(x))))
        else:
            raise ValueError("freq outside correct range")

    def set_frange(self,
                   fstart_num=None, fstart_ord=None,
                   fend_num=None, fend_ord=None):
        try:
            self.fstart = '%.0E' % (int(fstart_num) * fstart_ord)
            self.fstop = '%.0E' % (int(fend_num) * fend_ord)
        except:
            while True:
                try:
                    fstart = int(input("Enter start frequency: "))
                    fend = int(input("Enter end frequency: "))
                    self.fstart = '%.0E' % self.sig_fig_1(fstart)
                    self.fend = '%.0E' % self.sig_fig_1(fend)
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
