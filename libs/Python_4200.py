import matplotlib.pyplot as plt
import csv
import visa
import serial

from libs import cm110
from libs import ki4200
from libs import shutter
from serial.tools import list_ports
from IPython import display
from math import log10, floor
from time import sleep, strftime
from os import path, getcwd, makedirs
from re import sub


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
    lia5302_address = "GPIB0::12::INSTR"
    mono_port = ""
    shutter_port = ""
    cust_name = ""
    run_all = False
    last_test = "_"
    lia_freq = 0
    lia_mag = 0
    lia_pha = 0
    running = False

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            self.name = value
        self.repetitions = 3

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
        try:
            self.label = str(label)
        except:
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
        print("This method has been depreciated, use auto discovery")
        if instrument == "K4200":
            self.k4200_address = address
        elif instrument == "LS331":
            self.ls331_address = address

    def set_repetitions(self, repetitions):
        try:
            self.repetitions = int(repetitions)
        except:
            self.repetitions = int(input("Enter No. or repetitions: "))

    def com_discovery(self, *args):
        """
        ------------------------------------------------------------------------
        FUNCTION: com_discovery
        INPUTS: None
        RETURNS: offline_mode (bool)
                 result, default (str)
        DEPENDENCIES: serial
        ------------------------------------------------------------------------
        CHANGE THIS
        ------------------------------------------------------------------------
        """
        K4200_test.com_okay = False
        K4200_test.ard_default = "Offline"
        K4200_test.mono_default = "Offline"
        K4200_test.result = ["Offline"]
        com_ports = list(list_ports.comports())

        if not com_ports:
            K4200_test.result = ["No Ports"]
            K4200_test.ard_default = "No Ports"
            K4200_test.mono_default = "No Ports"
            K4200_test.com_okay = False
        else:
            K4200_test.result = []
            for port in com_ports:
                K4200_test.result.append(port[0])
                if "Arduino" in port[1]:
                    K4200_test.com_okay = True
                    K4200_test.ard_default = port[0]

                else:
                    try:
                        ser = serial.Serial(port[0])
                        ser.write(b'27')
                        sleep(0.1)
                        # Can't decode this, but only CM110 will reply this way
                        if ser.read(ser.inWaiting()) == b'\xa2\x18':
                            K4200_test.mono_default = port[0]
                        ser.close()
                    except:
                        pass

            if not K4200_test.com_okay:
                K4200_test.result.append("No Shutter")
                K4200_test.ard_default = "No Shutter"

    def visa_discovery(self):
        all_resources = K4200_test.rm.list_resources()
        K4200_test.visa_resources = (
            [i for i in all_resources if "ASRL" not in i])
        names = ['MODEL331S',
                 'MODEL 2440',
                 '34970A',
                 '5302',
                 'KI4200',
                 'HP6634A']
        queries = ['ID?', '*IDN?', 'ID']
        K4200_test.visa_okay = True
        if K4200_test.visa_resources:
            while True:
                K4200_test.instrs = {}
                for address in K4200_test.visa_resources:
                    try:
                        instr = K4200_test.rm.open_resource(address)
                        instr.timeout = 4
                        instr.clear()
                        sleep(0.3)
                    except:
                        print("Could not open resource")
                        continue
                    for q in queries:
                        try:
                            temp = instr.query(q, delay=0.05).strip('\n\r')
                            break
                        except:
                            pass
                    for name in names:
                        if name in temp:
                            K4200_test.instrs[name] = address
                    instr.close()
                if 'KI4200' in K4200_test.instrs.keys():
                    break
                else:
                    sleep(1)
        else:
            K4200_test.visa_okay = False
            K4200_test.visa_resources = ["No resources"]
            K4200_test.instrs = {}
            K4200_test.instrs['KI4200'] = "No resources"
            K4200_test.instrs['MODEL331S'] = "No resources"
            K4200_test.instrs['5302'] = "No resources"

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
        if instrument.upper() == "K4200":
            self.k4200 = self.rm.open_resource(self.k4200_address)
            try:
                assert "KI4200" in self.k4200.query("ID")
            except AssertionError:
                self.k4200.close()
                print("KI4200 not detected at given address")

            if self.mode == "iv":
                switch = 3
            else:
                switch = 1

            ki4200.init_4200(
                self.last_test not in self.mode, switch, self.k4200)

        elif instrument.upper() == "LS331":
            self.ls331 = self.rm.open_resource(self.ls331_address)
            try:
                assert "MODEL331S" in self.ls331.query("*IDN?")
            except AssertionError:
                self.ls331.close()
                print("LS331 not detected at given address")

        elif instrument.upper() == "LIA5302":
            self.lia5302 = self.rm.open_resource(self.lia5302_address)
            self.lia5302.query_delay = 0.05
            try:
                assert "5302" in self.lia5302.query("ID?")
            except AssertionError:
                self.lia5302.close()
                print("5302LIA not detected at given address")

    def set_shutter_port(self, p):
        K4200_test.shutter_port = p

    def set_mono_port(self, p):
        K4200_test.mono_port = p

    def set_custom_name(self, name):
        if name == "":
            self.cust_name = ""
        else:
            self.cust_name = (sub('[\/:*?"<>| ]', '',
                                  "_" + str(name)).rstrip())

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
        if step > abs(end - start) or end == start:
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

    def set_path(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.folder = path.join(getcwd(), "data/" + self.date)
        if not path.exists(self.folder):
            makedirs(self.folder)
        self.filename = self.time + "_" + self.mode + "_"
        t_type = "multi" if self.wrange_set else "single"
        self.filename += t_type + self.cust_name + ".csv"
        self.final_path = path.join(self.folder, self.filename)

    def save_to_csv(self, x_name, y_name, x, y, **kwargs):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        header = [x_name]
        data = []
        if isinstance(y[0], list):
            data = [x] + list(zip(*y))
            if "f" in self.mode:
                for f in self.yaxis:
                    header.append(str(f) + " Hz")
            else:
                for v in self.yaxis:
                    header.append(str(v) + " V")
        else:
            data = [x, y]
            header.append(y_name)

        for name, value in kwargs.items():
            if isinstance(value[0], list):
                header += name
                data += value
            else:
                header.append(name)
                data.append(value)

        self.set_path()
        with open(self.final_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(zip(*data))
            csvfile.close()

    def multi_graph(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        ylabel = "Capacitance (F)"
        if self.mode == "cv":
            if self.vrange_set:
                title = "CVW sweep"
            else:
                title = "CW sweep at {0} Volts".format(self.single_v)
        elif self.mode == "cf":
            title = "CFW sweep"
        elif self.mode == "iv":
            ylabel = "Current (A)"
            title = "IV sweep"

        ylabels = [ylabel, "Temperature (C)",
                   "Magnitude (%)", "Phase (°)"]
        titles = [title, "Temperature", "Magnitude", "Phase"]

        axes = []
        for i in range(4):
            axes.append(plt.subplot(221+i))

            axes[i].set_title(titles[i], fontsize=20, family="serif")
            axes[i].set_ylabel(ylabels[i], fontsize=14)
            axes[i].set_xlabel("Wavelength (Angstoms)", fontsize=14)

            axes[i].minorticks_on()
            axes[i].grid(b=True, which='major', color='#6C7A89')
            axes[i].grid(b=True, which='minor', color='#D2D7D3')

            axes[i].plot()

        axes[3].set_ylim([-180, 0])
        plt.tight_layout(h_pad=1.0)

        display.display(plt.gcf())
        display.clear_output(wait=True)
        self.axes = axes
        return 0

    def single_graph(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        ax = plt.subplot(111)

        ax.minorticks_on()
        ax.grid(b=True, which='major', color='#6C7A89')
        ax.grid(b=True, which='minor', color='#D2D7D3')

        ax.set_xlabel("Voltage (V)", fontsize=14)
        ax.set_ylabel("Capacitance (F)", fontsize=14)
        ax.set_title(
            "{0} sweep at {1} nm".format(
                self.mode.upper(),
                self.single_w_val/10),
            fontsize=20,
            family="serif")

        if self.mode == "cv":
            ax.plot()
        elif self.mode == "cf":
            ax.set_xlabel("Frequency (Hz)")
            ax.semilogx()
        elif self.mode == "iv":
            ax.set_ylabel("Current (A)")
            ax.plot()
        display.display(plt.gcf())
        display.clear_output(wait=True)
        self.ax = ax
        return 1

    def setup_graph(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        plt.clf()
        plt.close()
        plt.figure(
            num=1,
            figsize=(14, 10),
            dpi=80,
            facecolor='w',
            edgecolor='k')

        if self.wrange_set:
            self.multi_graph()
        else:
            self.single_graph()

    def cvf_commands(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.commands = [":CVU:RESET",
                         ":CVU:MODE 1",
                         ":CVU:MODEL " + str(self.model),
                         ":CVU:SPEED " + str(self.speed),
                         ":CVU:ACV " + str(self.acv),
                         ":CVU:SOAK:DCV " + str(self.dcvsoak),
                         ":CVU:ACZ:RANGE " + self.acz,
                         ":CVU:CORRECT " + self.comps,
                         ":CVU:LENGTH " + str(self.length),
                         ":CVU:STANDBY 1",
                         ":CVU:DELAY:SWEEP " + str(self.delay)]
        if self.mode == "cv":
            self.commands.append(
                ":CVU:FREQ {0}".format(self.freq))
            self.commands.append(
                ":CVU:SWEEP:DCV {0},{1},{2}".format(self.vstart,
                                                    self.vend,
                                                    self.vstep))
        elif self.mode == "cf":
            self.commands.append(
                ":CVU:SWEEP:FREQ {0},{1}".format(self.fstart,
                                                 self.fstop))

    def ct_commands(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.commands = [":CVU:MODE 0",
                         ":CVU:RESET",
                         ":CVU:MODEL " + str(self.model),
                         ":CVU:SPEED " + str(self.speed),
                         ":CVU:ACV " + str(self.acv),
                         ":CVU:FREQ " + self.freq,
                         ":CVU:DCV " + str(self.single_v),
                         ":CVU:ACZ:RANGE " + self.acz,
                         ":CVU:CORRECT " + self.comps,
                         ":CVU:LENGTH " + str(self.length)]

    def iv_commands(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        self.commands = [
            "DE", "DR1", "CH1;CH2", "CH1,'VA','IA',1,1",
            "CH2,'VC','IC',3,3", "SS",
            "VR1,{0},{1},{2},{3}".format(self.vstart, self.vend,
                                         self.vstep, self.compliance),
            "DT {0}".format(self.delay),
            "IT {0}".format(self.speed),
            "RS {0}".format(self.sig_fig),
            "RG 1, {0}".format(self.min_cur),
            "SM DM2", "LI 'VA','IA'", "MD"]

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
        if self.vrange_set and self.mode != "ct":
            (self.cvf_commands() if self.mode in
             ("cv", "cf") else self.iv_commands())
        elif self.mode != "ct":
            self.iv_commands()
        else:
            return -1

        self.set_visa_instr(instrument="K4200")
        for c in self.commands:
            self.k4200.write(c)

        self.set_visa_instr(instrument="LIA5302")

        cm = cm110.mono(port=self.mono_port)
        sh = shutter.ard_shutter(port=self.shutter_port)
        self.setup_graph()
        if self.wrange_set:
            self.set_visa_instr(instrument="LS331")
            self.ls331.timeout = 0.1
        return cm, sh

    def cv_no_v(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        data = []
        t = []
        mag = []
        pha = []
        for r in range(int(self.repetitions)):
            self.k4200.write(":CVU:TEST:RUN")
            self.k4200.wait_for_srq()
            self.k4200.write(':CVU:DATA:Z?')
            self.lia_freq = (float(self.lia5302.query('FRQ'))/1000)
            mag.append(float(self.lia5302.query('MAG'))/100)
            pha.append(float(self.lia5302.query('PHA'))/1000)
            values = self.k4200.read(termination=",\r\n", encoding="utf-8")
            p, s = ki4200.CV_output_san(values)
            data.append(p)
            try:
                t.append(float(self.ls331.query('KRDG?').replace('+', '')))
            except:
                t.append(0)
        self.mag.append(sum(mag)/len(mag))
        self.pha.append(sum(pha)/len(pha))
        self.temp.append(sum(t)/len(t))
        avg = [sum(col) / len(col) for col in zip(*data)]
        self.prim.append(avg)
        self.sec.append(s)

    def cv_v(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        data = []
        t = []
        mag = []
        pha = []
        for r in range(int(self.repetitions)):
            data.append(
                float(self.k4200.query(":CVU:MEASZ?").split(',').pop(0)))
            mag.append(float(self.lia5302.query('MAG'))/100)
            pha.append(float(self.lia5302.query('PHA'))/1000)
            try:
                t.append(float(self.ls331.query('KRDG?').replace('+', '')))
            except:
                t.append(0)
        self.mag.append(sum(mag)/len(mag))
        self.pha.append(sum(pha)/len(pha))
        self.temp.append(sum(t)/len(t))
        if int(self.repetitions) > 1:
            self.prim.append(sum(data)/len(data))

    def iv(self):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        data = []
        t = []
        mag = []
        pha = []
        for r in range(int(self.repetitions)):
            self.k4200.write("ME1")
            self.k4200.wait_for_srq(timeout=None)
            out = self.k4200.query("DO 'IA'")
            data.append([float(d) for d in sub(
                '[N]', '', out).split(',')])
            try:
                t.append(float(self.ls331.query('KRDG?').replace('+', '')))
            except:
                t.append(0)
            self.lia_freq = (int(self.lia5302.query('FRQ'))/1000)
            self.lia_mag = (int(self.lia5302.query('MAG'))/100)
            self.lia_pha = (int(self.lia5302.query('PHA'))/1000)
            mag.append(self.lia_mag)
            pha.append(self.lia_pha)
        self.mag.append(sum(mag)/len(mag))
        self.pha.append(sum(pha)/len(pha))
        self.temp.append(sum(t)/len(t))
        avg = [sum(col) / len(col) for col in zip(*data)]
        self.prim.append(avg)

    def re_plot(self, w):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: self
        RETURNS:
        DEPENDENCIES:
        ------------------------------------------------------------------------

        ------------------------------------------------------------------------
        """
        colours = ["g", "b", "r", "c", "m", "y", "k"]
        if w > self.wstart:
            del(self.axes[1].lines[-1])
            del(self.axes[2].lines[-1])
            del(self.axes[3].lines[-1])
        self.axes[1].plot(self.wavelengths, self.temp, 'b-')
        self.axes[2].plot(self.wavelengths, self.mag, 'r-')
        self.axes[3].plot(self.wavelengths, self.pha, 'g-')
        if self.vrange_set or self.mode == "cf":
            self.y = (list(map(list, zip(*self.prim))))
            i = 0
            for line in self.y:
                if w > self.wstart:
                    del(self.axes[0].lines[-len(self.y)])
                if i < 7:
                    self.axes[0].plot(self.wavelengths, line, colours[i])
                else:
                    self.axes[0].plot(self.wavelengths, line)
                i += 1
        else:
            if w > self.wstart:
                del(self.axes[0].lines[-1])
            self.axes[0].plot(self.wavelengths, self.prim, 'b-')

        display.display(plt.gcf())
        display.clear_output(wait=True)

    def run_multi_sweep(self):
        pass

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
        self.running = True
        display.clear_output(wait=True)
        self.date = strftime("%Y-%m-%d")
        self.time = strftime("%H.%M.%S")
        t_type = "multi" if self.wrange_set else "single"
        imgname = ("data/" + self.date + "/" + self.time + "_" + self.mode
                   + "_" + t_type + self.cust_name + ".png")

        cm, sh = self.setup_test()

        self.prim = []
        self.sec = []
        self.yaxis = []
        self.temp = []
        self.mag = []
        self.pha = []

        if self.wrange_set:
            sh.open()
            self.wavelengths = []

            for w in range(self.wstart, self.wend+1, self.wstep):

                self.wait > 0.5 and sh.close()
                cm.command("goto", w)
                sleep(self.wait)
                self.wait > 0.5 and sh.open()

                if self.mode in ("cv, cf"):
                    if not (self.mode == "cv" and not self.vrange_set):
                        self.cv_no_v()
                    else:
                        self.cv_v()
                elif self.mode == "iv":
                    self.iv()

                self.wavelengths.append(w)
                self.re_plot(w)

            cm.close()
            sh.close()
            sh.shutdown()

            if self.mode == "cv" and self.vrange_set:
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.k4200)
            elif self.mode == "cf":
                self.yaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.k4200)
            elif self.mode == "iv":
                self.yaxis = sub('[N]',
                                 '', self.k4200.query("DO 'VA'")).split(',')
            self.k4200.close()
            self.save_to_csv(
                x_name="Wavelengths (A)", x=self.wavelengths,
                y_name="Voltage (V)", y=self.prim,
                temperature=self.temp,
                phase=self.pha,
                magnitude=self.mag)

            plt.savefig(imgname)
            self.running = False
            return 0

        else:
            cm.command("goto", self.single_w_val)
            cm.close()
            sleep(1)
            sh.open()
            data = []
            for r in range(int(self.repetitions)):
                if self.mode in ("cv", "cf"):
                    self.k4200.write(":CVU:TEST:RUN")
                    self.k4200.wait_for_srq(timeout=None)
                    self.k4200.write(':CVU:DATA:Z?')
                    values = self.k4200.read(
                        termination=",\r\n", encoding="utf-8")
                    d, sec = ki4200.CV_output_san(values)
                    data.append(d)
                else:
                    self.k4200.write("ME1")
                    self.k4200.wait_for_srq(timeout=None)
                    out = self.k4200.query("DO 'IA'")
                    data.append([float(d) for d in sub(
                        '[N]', '', out).split(',')])
            if int(self.repetitions) > 1:
                self.prim = [sum(col) / len(col) for col in zip(*data)]
            if self.mode == "cv":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:VOLT?', self.k4200)
                xname = "Voltage"
                yname = "Capacitance"
            elif self.mode == "cf":
                self.xaxis = ki4200.read_4200_x(':CVU:DATA:FREQ?', self.k4200)
                xname = "Frequency"
                yname = "Capacitance"
            elif self.mode == "iv":
                self.xaxis = sub('[N]',
                                 '', self.k4200.query("DO 'VA'")).split(',')
                xname = "Voltage"
                yname = "Current"
            self.ax.plot(self.xaxis, self.prim)
            self.k4200.close()
            sh.close()
            sh.shutdown()

            self.save_to_csv(
                x_name=xname, x=self.xaxis,
                y_name=yname, y=self.prim)

            display.display(plt.gcf())
            display.clear_output(wait=True)
            plt.savefig(imgname)
            self.running = False
            return 0


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

    def set_comps(self, open, short, load):
        self.comps = (str(int(open)) + "," + str(int(short)) +
                      "," + str(int(load)))


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
        self.vrange_set = True
        self.vstart = -5
        self.vend = 5
        self.vstep = 1
        self.freq = freq
        self.single_v = 0
        self.mode = "cv"
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

    def set_single_v(self, v):
        self.single_v = v
        self.vrange_set = False

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
        self.mode = "cf"
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


class iv_test(K4200_test):

    """
    ---------------------------------------------------------------------------
     _____  __      __  _______   ______    _____   _______
    |_   _| \ \    / / |__   __| |  ____|  / ____| |__   __|
      | |    \ \  / /     | |    | |__    | (___      | |
      | |     \ \/ /      | |    |  __|    \___ \     | |
     _| |_     \  /       | |    | |____   ____) |    | |
    |_____|     \/        |_|    |______| |_____/     |_|
    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------

    ---------------------------------------------------------------------------
    """

    def __init__(self, label, speed=2, delay=0, mono_port="COM1", wait=1,
                 shutter_port="COM12"):
        self.label = label
        self.speed = speed
        self.delay = delay
        self.vstart = 0
        self.vend = 5
        self.vstep = 1
        self.compliance = "100E-3"
        self.sig_fig = 5
        self.min_cur = "1E-3"
        self.repetitions = 1
        self.vrange_set = False
        self.mode = "iv"
        K4200_test.__init__(
            self, label=label, speed=speed, delay=delay, mono_port=mono_port,
            shutter_port=shutter_port, mode="iv", wait=wait)

    def set_single_v(self, v):
        self.single_v = v
        self.vrange_set = False

    def set_min_cur(self, num, order):
        self.min_cur = str(num) + order

    def set_compliance(self, compliance):
        if compliance == 0:
            self.compliance = 0
        else:
            compliance = compliance/1000
            self.compliance = '%.0E' % compliance

    def set_sig_fig(self, sig_fig):
        self.sig_fig = sig_fig

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


def save_to_csv_old(self, xdata, ydata, zdata=None):

    if self.mode in ("cv", "iv"):
        if self.wrange_set:
            header = ["Wavelength (A)"]
            for v in self.yaxis:
                header.append(str(v) + "V")
            data = []
            for i in range(len(ydata)):
                if self.vrange_set:
                    ydata[i].insert(0, xdata[i])
                    ydata[i].append(zdata[i])
                    data = ydata
                else:
                    data.append([xdata[i], ydata[i], zdata[i]])
            if not self.vrange_set:
                header.append("Capacitance (F)")
            header.append("Temperature (K)")
        else:
            if self.mode == "cv":
                header = ["Voltage", "Capacitance"]
            else:
                header = ["Voltage", "Current"]
            data = ([[xdata[i], ydata[i]] for i in range(len(xdata))])

    elif self.mode == 'cf':
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

    self.folder = path.join(getcwd(), "data/" + self.date)
    if not path.exists(self.folder):
        makedirs(self.folder)

    self.filename = self.time + "_" + self.mode + "_"
    if self.wrange_set:
        self.filename += "multi" + self.cust_name + ".csv"
    else:
        self.filename += "single" + self.cust_name + ".csv"
    self.final_path = path.join(self.folder, self.filename)
    with open(self.final_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)
        csvfile.close()

# If running this library, print doc string for all functions
if __name__ == "__main__":
    print("library imported")
