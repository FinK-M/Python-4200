import visa
import csv
from time import sleep
from Python_4200 import select_device


class routine(object):

    instances = 0
    routines = []
    csv_params = []

    def __init__(self, name, delay=1, steps=5, low_f=50, high_f=100):
        routine.instances += 1
        self.name = name
        self.delay = delay
        self.steps = steps
        self.low_f = low_f
        self.high_f = high_f

    def parameters(self):
        self.description = "{0}: delay {1} s, {2} steps, start f {3}Hz, end f {4}Hz".format(self.name, self.delay, self.steps, self.low_f, self.high_f)
        print(self.description)

    def set_delay(self, delay=0):

        if type(delay) != int and type(delay) != float:
            raise ValueError("Delay must be a float or int")

        if delay >= 1:
            self.delay = delay

        else:
            while True:
                try:
                    self.delay = float(input("Enter delay in seconds (1 or greater): "))
                    if self.delay < 1:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter valid delay...")

    def set_steps(self, steps=0):

        if type(steps) != int:
            raise ValueError("Enter a postive integer number of steps")

        if steps >= 1:
            self.steps = steps

        else:
            while True:
                try:
                    self.steps = int(input("Enter number of steps (1 or greater): "))
                    if self.steps < 1:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter valid number of steps...")

    def set_low_f(self, low_f=0):

        if type(low_f) != int:
            raise ValueError("Enter integer value between 40 and 300Hz")

        if low_f >= 40 and low_f <= 300:
            self.low_f = low_f

        else:
            while True:
                try:
                    self.low_f = int(input("Enter low frequency in Hz (40 < f < 400): "))
                    if self.low_f < 40 or self.low_f > 399:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter valid frequency...")

    def set_high_f(self, high_f=0):

        if type(high_f) != int:
            raise ValueError("Enter integer value between 100 and 400Hz")

        if high_f >= 100 and high_f <= 400:
            self.high_f = high_f

        else:
            while True:
                try:
                    self.high_f = int(input("Enter high frequency in Hz (50 < f < 400): "))
                    if self.high_f < 50 or self.high_f > 400:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter valid frequency...")

    def run(self, instr):
        self.step_size = int((self.high_f - self.low_f)/self.steps)
        for f in range(int(self.low_f), int(self.high_f + 1), self.step_size):
            Vout = (f - 2.1333)/42.139
            instr.write("VSET " + str(Vout))
            print(f, "VSET " + str(Vout))
            sleep(self.delay)
        instr.write("VSET 0")

    def update(self):
        self.params = [self.name, self.delay, self.steps, self.low_f, self.high_f]
        routine.csv_params.append(self.params)
        routine.routines.append(self)


def create_routine():
    name = input("Please enter the name for this routine: ")
    r = routine(name)
    r.set_delay()
    r.set_steps()
    r.set_low_f()
    r.set_high_f()
    r.update()


def save_routines():
    with open('settings.csv', 'w', newline='') as csvfile:
        reswrite = csv.writer(csvfile)
        for row in routine.csv_params:
            reswrite.writerow(row)
        csvfile.close()


def open_routines():
    try:
        with open('settings.csv', 'r', newline='') as csvfile:
            resread = csv.reader(csvfile)
            for row in resread:
                r = (routine(row[0], "i"))
                r.name = row[0]
                r.delay = float(row[1])
                r.steps = int(row[2])
                r.low_f = int(row[3])
                r.high_f = int(row[4])
                r.update()
            csvfile.close()
    except:
        print("No previous routines detected")


if __name__ == "__main__":

    rm = visa.ResourceManager()
    addr = select_device(rm)
    instr = rm.open_resource(addr)
    instr.clear()
    sleep(1)
    instr.write("VSET 1")
    open_routines()
    while True:
        i = 0
        for r in routine.routines:
            print(i, ": ", end='')
            r.parameters()
            i += 1

        if i == 0:
            print("Please create a first routine")
            selection = 0
            create_routine()
        else:
            print(i, ": Create new routine")
            selection = int(input("Make a selection: "))
            if selection == i:
                create_routine()

        active = routine.routines[selection]
        active.run(instr)

        if input("Exit? (y/n) : ").lower() == "y":
            break

    save_routines()
    instr.close()
