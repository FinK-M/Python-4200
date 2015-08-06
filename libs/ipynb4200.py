from IPython.html import widgets
from IPython.display import display
from threading import Timer
from libs import Python_4200
from time import sleep, strftime


class CIVW_GUI(object):

    def __init__(self):
        self.master = Python_4200.K4200_test()
        self.iv_test = Python_4200.iv_test("iv_test")
        self.cf_test = Python_4200.cf_test("cf_test")
        self.cv_test = Python_4200.cv_test("cv_test")

    def test_update(self, test, **kwargs):
        for name, value in kwargs.items():
            setattr(test, name, value)

    def cap_test_update(self, **kwargs):
        for name, value in kwargs.items():
            setattr(Python_4200.cap_test, name, value)

    def K4200_class_update(self, **kwargs):
        """
        This function is used to update or add any class variable within the
        K4200_test class that does not have an explicit method to do so already
        """
        for name, value in kwargs.items():
            setattr(Python_4200.K4200_test, name, value)

    def v_sliders(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION: v_sliders
        INPUTS: test (Python_4200.test)
        RETURNS: widgets.Box
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        Generates three sliders for the selection of start/end voltages, and
        voltage step. Adds a description to each then packages them in a box
        widget which is then returned.
        ------------------------------------------------------------------------
        """
        vstep_select = widgets.BoundedFloatText(
            min=0.01, max=10, value=1,
            margin=10,
            width=50,
            description="Step")

        vstart_select = widgets.BoundedIntText(
            min=-30, max=30, value=-5,
            margin=10,
            width=50,
            description="Start")

        vend_select = widgets.BoundedIntText(
            min=-30, max=30, value=5,
            margin=10,
            width=50,
            description="End")

        vsingle_select = widgets.BoundedFloatText(
            min=-30, max=30, value=0,
            margin=10,
            width=50,
            description="Voltage")

        if test.mode == "cv":
            description = widgets.HTML(value="""
            <h3>Capacitance-Voltage sweep configuration</h3>
            <p>Start and end voltages can be between -30.00V and 30.00V.</p>
            <p>Step voltage can be between 0.01V and 5V.</p>
            """, margin=5)

        elif test.mode == "iv":
            vstart_select.max = vend_select.max = vsingle_select.max = 210
            vstart_select.min = vend_select.min = vsingle_select.min = -210
            description = widgets.HTML(value="""
            <h3>Current-Voltage sweep configuration</h3>
            <p>Start and end voltages can be between -210.00V and 210.00V.</p>
            <p>Step voltage can also be anywhere in this range.</p>
            """, margin=5)

        single_box = widgets.VBox(
            children=[vsingle_select],
            height=150,
            visible=False)

        widgets.interactive(
            test.set_vrange,
            vstart=vstart_select,
            vend=vend_select,
            vstep=vstep_select)

        widgets.interactive(
            test.set_single_v,
            v=vsingle_select)

        selectors = widgets.VBox(
            children=[vstart_select, vstep_select, vend_select],
            align="start",
            height=150)

        def one_or_many(value):
            if value:
                single_box.visible = True
                selectors.visible = False
                test.vrange_set = False
            else:
                single_box.visible = False
                selectors.visible = True
                test.vrange_set = True

        single_v = widgets.Checkbox(
            description="Single Voltage?",
            value=False,
            margin=10)
        widgets.interactive(one_or_many, value=single_v)

        if test.mode == "iv":
            single_v.visible = False

        return widgets.HBox(
            children=[selectors, single_box, description, single_v],
            margin=20,
            align="center")

    def w_sliders(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION: w_sliders
        INPUTS: test (Python_4200.test)
        RETURNS: widgets.Box
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        Generates four sliders for the selection of start/end wavelengths,
        wavelength step, and single wavelength. Adds a description to each.
        Also creates a single or many wavelength selector with corresponding
        function hide sliders. Tick box and all sliders are packaged in a
        widget box and returned
        ------------------------------------------------------------------------
        """

        wstep_slider = widgets.IntSlider(
            min=50, max=500, step=50, value=250,
            description="Wavelength Step")

        wstart_slider = widgets.IntSlider(
            min=3000, max=8000, step=100, value=5000,
            description="Start Wavelength")

        wend_slider = widgets.IntSlider(
            min=3000, max=8000, step=100, value=5500,
            description="End Wavelength")

        single_w = widgets.Checkbox(
            description="Single Wavelength:",
            value=False)

        single_w_slider = widgets.IntSlider(
            description="Wavelength",
            min=300,
            max=8000,
            step=100,
            value=5500)

        single_wavelength_set = widgets.interactive(
            test.set_single_w,
            w=single_w_slider)
        single_wavelength_set.visible = False

        wavelength_sliders = widgets.interactive(
            test.set_wavelengths,
            wstart=wstart_slider,
            wend=wend_slider,
            wstep=wstep_slider)
        wavelength_sliders.visible = True

        def one_or_many(name, value):
            if value:
                wavelength_sliders.visible = False
                single_wavelength_set.visible = True
                test.wrange_set = False
            else:
                wavelength_sliders.visible = True
                single_wavelength_set.visible = False
                test.wrange_set = True

        single_w.on_trait_change(one_or_many, 'value')

        return widgets.Box(
            children=[single_w, wavelength_sliders, single_wavelength_set],
            height=200,
            margin=20,
            align="center")

    def delays(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION: delays
        INPUTS: test (Python_4200.test)
        RETURNS: widgets.Box
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        Generates four sliders for the selection of shutter and sweep delays
        and adds a description to each. Also creates two HTML widgets to
        provide a small subtitle to explain the purpose of the two pairs of
        sliders.
        ------------------------------------------------------------------------
        """
        minute_wait_slider = widgets.IntSlider(
            min=0, max=60, step=1, value=0,
            description="Minutes")

        second_wait_slider = widgets.IntSlider(
            min=0, max=60, step=1, value=0,
            description="Seconds")

        delay_slider = widgets.IntSlider(
            min=0, max=60, step=1, value=0,
            description="Seconds")

        wait_text = widgets.HTML(
            value="Select time in minutes and seconds that " +
            "shutter closes for between voltage sweeps",
            margin=10)

        delay_text = widgets.HTML(
            value="Select time delay between each voltage level in each sweep",
            margin=10)

        set_delay = widgets.interactive(
            test.set_delay,
            delay=delay_slider)

        set_wait = widgets.interactive(
            test.set_wait,
            wait_sec=second_wait_slider,
            wait_min=minute_wait_slider)

        return widgets.Box(
            children=[wait_text, set_wait, delay_text, set_delay],
            margin=20,
            align="center")

    def visa_selector(self):
        self.master.visa_discovery()
        print(self.master.instrs['KI4200'],  self.master.visa_resources)
        self.K4200_select = widgets.Dropdown(
            options=self.master.visa_resources,
            value=self.master.instrs['KI4200'],
            description="4200 SCS address",
            margin=5)

        self.LS331_select = widgets.Dropdown(
            options=self.master.visa_resources,
            value=self.master.instrs['MODEL331S'],
            description="LS 331 address",
            margin=5)

        self.LIA5302_select = widgets.Dropdown(
            options=self.master.visa_resources,
            value=self.master.instrs['5302'],
            description="5302 LIA address",
            margin=5)

        widgets.interactive(
            self.K4200_class_update,
            k4200_address=self.K4200_select,
            ls331_address=self.LS331_select,
            lia5302_address=self.LIA5302_select)

        visa_select = widgets.VBox(
            children=[self.K4200_select,
                      self.LS331_select,
                      self.LIA5302_select],
            align="end",
            margin=10)

        return visa_select

    def com_selectors(self, *args):
        """
        ------------------------------------------------------------------------
        FUNCTION: com_selectors
        INPUTS: test (Python_4200.test)
        RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
                 offline_mode (bool)
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        Takes the available COM ports generated by the com_discovery function
        and puts them into two drop down menu widgets, returns these two
        widgets, and forwards the off-line mode variable.
        ------------------------------------------------------------------------
        """
        self.master.com_discovery()
        self.mono_com_select = widgets.Dropdown(
            options=self.master.result,
            description="Monochromator port",
            margin=5)

        self.ard_com_select = widgets.Dropdown(
            options=self.master.result,
            description="Arduino Shutter port",
            value=self.master.ard_default,
            margin=5)

        self.K4200_class_update(
            mono_port="COM1",
            shutter_port=self.master.ard_default)

        widgets.interactive(
            self.K4200_class_update,
            mono_port=self.mono_com_select,
            shutter_port=self.ard_com_select)

        com_select = widgets.VBox(
            children=[self.mono_com_select, self.ard_com_select],
            align="end",
            margin=10)

        return com_select

    def equipment_config(self):
        """
        ------------------------------------------------------------------------
        FUNCTION: equipment_config
        INPUTS: None
        RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
                 offline_mode (bool)
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        Takes the two COM port drop down menus, and adds them to a VBox widget
        along with a length select drop down. Formats the Vbox to centre the
        menus and adds a white border. Then returns this Vbox
        ------------------------------------------------------------------------
       """
        self.com_visa_select = widgets.HBox(
            children=[self.com_selectors(), self.visa_selector()],
            height=100,
            margin=20,
            align="center")

        def update(name):
            self.master.com_discovery()
            self.master.visa_discovery()
            self.mono_com_select.options = self.master.result
            self.ard_com_select.options = self.master.result
            self.ard_com_select.value = self.master.ard_default
            self.K4200_select.options = self.master.visa_resources
            self.LS331_select.options = self.master.visa_resources
            self.LIA5302_select.options = self.master.visa_resources
            self.K4200_select.value = self.master.instrs['KI4200']
            self.LS331_select.value = self.master.instrs['MODEL331S']
            self.LIA5302_select.value = self.master.instrs['5302']
            offline_mode = self.master.com_okay and self.master.visa_okay
            self.oneall_tick.visible = offline_mode
            self.start_button.visible = offline_mode

        self.re_check = widgets.Button(
            description="Update",
            margin=30)
        self.re_check.on_click(update)

        return widgets.VBox(
            children=[self.re_check, self.com_visa_select],
            align="center")

    def ac_volt(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        acv_slider = widgets.IntSlider(
            min=10, max=100, step=1, value=30,
            description="AC ripple voltage (mV)",
            margin=10)
        widgets.interactive(test.set_acv, acv=acv_slider)

        return acv_slider

    def ac_range(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        acz_range = widgets.Dropdown(
            options={"Auto": "0",
                     "1µA": "1E-6",
                     "30µA": "30E-6",
                     "1mA": "1E-3"},
            value="0",
            align="end",
            description="Current Range",
            margin=5)
        widgets.interactive(test.set_acz, acz=acz_range)

        return acz_range

    def ac_freq(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        one_to_ten = [str(i) for i in range(1, 11)]
        order = {"1K": 1000, "10K": 10000, "100K": 100000, "1M": 1000000}

        freq_num = widgets.Dropdown(
            options=one_to_ten,
            value="1",
            description="Frequency",
            margin=5)

        freq_order = widgets.Dropdown(
            options=order,
            value=1000000,
            description="Order",
            margin=5)

        if test.mode == "cv":
            widgets.interactive(
                test.set_freq,
                f_num=freq_num,
                f_order=freq_order)

            return freq_num, freq_order

        elif test.mode == "cf":

            freq_num2 = widgets.Dropdown(
                options=one_to_ten,
                value="3",
                description="Frequency",
                margin=5)

            freq_order2 = widgets.Dropdown(
                options=order,
                value=1000000,
                description="Order",
                margin=5)

            widgets.interactive(
                test.set_frange,
                fstart_num=freq_num,
                fstart_ord=freq_order,
                fend_num=freq_num2,
                fend_ord=freq_order2)

            freq_nums = widgets.HBox(
                children=[freq_num, freq_order],
                align="start")

            freq_ords = widgets.HBox(
                children=[freq_num2, freq_order2],
                align="start")

            start = widgets.HTML(
                value="<b>Start Value</b>",
                margin=5)

            end = widgets.HTML(
                value="<b>End Value</b>",
                margin=5)

            return widgets.VBox(
                children=[start, freq_nums, end, freq_ords],
                margin=20,
                align="center")

    def speed(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        speed_menu = widgets.Dropdown(
            options={"Fast": 0, "Normal": 1, "Quiet": 2},
            value=1,
            description="Integration speed",
            align="end",
            margin=5)
        widgets.interactive(test.set_speed, speed=speed_menu)

        return speed_menu

    def comps(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        open_comp = widgets.Checkbox(
            description="Open",
            value=False)

        short_comp = widgets.Checkbox(
            description="Short",
            value=False)

        load_comp = widgets.Checkbox(
            description="Load",
            value=False)

        comps = widgets.HBox(
            children=[open_comp, short_comp, load_comp],
            width=290)

        widgets.interactive(
            test.set_comps,
            open=open_comp,
            short=short_comp,
            load=load_comp,
            margin=10)

        comp_description = widgets.HTML(value="Select test compensations")

        comp_box = widgets.VBox(
            children=[comp_description, comps],
            margin=20,
            align="center")

        return comp_box

    def repeat_select(self, test):
        one_to_ten = [str(i) for i in range(1, 11)]

        repeat_menu = widgets.Dropdown(
            options=one_to_ten,
            value="3",
            description="Repetitions",
            margin=5)

        widgets.interactive(
            test.set_repetitions,
            repetitions=repeat_menu)

        return repeat_menu

    def iv_test_params(self, test):
        order = ["E" + str(i) for i in range(-3, -13, -3)]

        compliance_select = widgets.BoundedFloatText(
            min=-105, max=105, value=100,
            margin=10,
            description="mA")

        sig_fig_select = widgets.IntSlider(
            min=3, max=7, value=5,
            margin=10,
            description="Significant Figures")

        min_cur_ord = widgets.Dropdown(
            options=order,
            value="E-3",
            description="Order",
            margin=10)

        min_cur_num = widgets.BoundedIntText(
            min=1, max=100,
            description="Current",
            margin=10,
            width=60)

        compliance_text = widgets.HTML(value="""
        Enter current compliance between -105mA and 105mA""")

        current_text = widgets.HTML(value="""
        Select minimum current to measure""")

        widgets.interactive(
            test.set_compliance,
            compliance=compliance_select)

        widgets.interactive(
            test.set_sig_fig,
            sig_fig=sig_fig_select)

        widgets.interactive(
            test.set_min_cur,
            num=min_cur_num,
            order=min_cur_ord)

        min_cur = widgets.HBox(
            children=[min_cur_num, min_cur_ord],
            align="end")

        return widgets.VBox(
            children=[compliance_text, compliance_select,
                      sig_fig_select, current_text, min_cur],
            margin=20,
            align="center")

    def cap_test_params(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        acz_range = self.ac_range(test)
        speed_menu = self.speed(test)
        comp_box = self.comps(test)
        acv_slider = self.ac_volt(test)

        length_menu = widgets.Dropdown(
            options=["0", "1.5", "3"],
            description="Cable Length",
            value="1.5",
            margin=5)

        widgets.interactive(
            test.set_length,
            length=length_menu)

        left_box = widgets.VBox(
            align="end",
            width=330)

        right_box = widgets.VBox(
            align="end",
            width=330)

        repeat_menu = self.repeat_select(test)

        if test.mode == "cv":
            freq_num, freq_order = self.ac_freq(test)
            left_box.children = [freq_num, acz_range, length_menu]
            right_box.children = [freq_order, speed_menu, repeat_menu]

        elif test.mode == "cf":
            left_box.children = [acz_range, length_menu]
            right_box.children = [speed_menu, repeat_menu]

        box = widgets.HBox(
            children=[left_box, right_box],
            align="end")

        return widgets.VBox(
            children=[acv_slider, box, comp_box],
            height=350,
            margin=20,
            align="center")

    def custom_name(self, test):
        """
        ------------------------------------------------------------------------
        FUNCTION:
        INPUTS: test (Python_4200.test)
        RETURNS:
        DEPENDENCIES: IPython.html.widgets
        ------------------------------------------------------------------------
        ------------------------------------------------------------------------
        """
        descriptor = widgets.HTML(
            value="<p>Enter a custom description for the file/s produced by " +
            "this test.</p>" +
            "<p>Leave blank to just use automatically generated tags.</p>",
            margin=10)

        name_input = widgets.Text(description="Custom Text")

        time = widgets.HTML(
            value="",
            margin=10)

        widgets.interactive(
            test.set_custom_name,
            name=name_input)

        def update():
            time.value = (
                "<b>Filename: </b>" + strftime("%H.%M.%S") +
                "_" + test.mode + test.cust_name + ".csv")
            Timer(.1, update).start()
        update()

        return widgets.Box(
            children=[descriptor, name_input, time],
            margin=20,
            align="center")

    def make_cv_tabs(self):
        cv_pages = [self.v_sliders(self.cv_test),
                    self.w_sliders(self.cv_test),
                    self.delays(self.cv_test),
                    self.cap_test_params(self.cv_test),
                    self.config_page,
                    self.custom_name(self.cv_test)]
        cv_tabs = widgets.Tab(
            children=cv_pages,
            description="")
        cv_tabs.set_title(0, 'Voltage Range')
        self.cv_tabs = cv_tabs

    def make_cf_tabs(self):
        cf_pages = [self.ac_freq(self.cf_test),
                    self.w_sliders(self.cf_test),
                    self.delays(self.cf_test),
                    self.cap_test_params(self.cf_test),
                    self.config_page,
                    self.custom_name(self.cf_test)]
        cf_tabs = widgets.Tab(
            children=cf_pages,
            description="")
        cf_tabs.set_title(0, 'Frequency Range')
        self.cf_tabs = cf_tabs

    def make_iv_tabs(self):
        iv_pages = [self.v_sliders(self.iv_test),
                    self.w_sliders(self.iv_test),
                    self.delays(self.iv_test),
                    self.iv_test_params(self.iv_test),
                    self.config_page,
                    self.custom_name(self.iv_test)]
        iv_tabs = widgets.Tab(
            children=iv_pages,
            description="")
        iv_tabs.set_title(0, 'Voltage Range')
        self.iv_tabs = iv_tabs

    def visible_tabs(self, mode):
        if mode == "CV":
            self.cv_tabs.visible = True
            self.cf_tabs.visible = False
            self.iv_tabs.visible = False

        elif mode == "CF":
            self.cv_tabs.visible = False
            self.cf_tabs.visible = True
            self.iv_tabs.visible = False

        elif mode == "IV":
            self.cv_tabs.visible = False
            self.cf_tabs.visible = False
            self.iv_tabs.visible = True

    def top_bar(self):
        self.start_button = widgets.Button(
            description="Run test",
            margin=20)
        self.start_button.on_click(self.start_test)

        self.oneall_tick = widgets.Checkbox(
            description="Run All?",
            margin=20)

        widgets.interactive(
            self.K4200_class_update,
            run_all=self.oneall_tick)

        self.select_types = widgets.ToggleButtons(
            options=["CV", "CF", "IV"],
            description="Test",
            margin=20)

        widgets.interactive(
            self.visible_tabs,
            mode=self.select_types)

        offline_mode = self.master.com_okay and self.master.visa_okay
        self.oneall_tick.visible = offline_mode
        self.start_button.visible = offline_mode
        top = widgets.HBox(children=[
            self.select_types,
            self.oneall_tick,
            self.start_button])
        display(top, self.cv_tabs, self.cf_tabs, self.iv_tabs)

    def start_test(self, name):
        if Python_4200.K4200_test.run_all:
            self.cv_test.run_test()
            Python_4200.K4200_test.last_test = "c"
            sleep(1)

            self.cf_test.run_test()
            Python_4200.K4200_test.last_test = "c"
            sleep(1)

            self.iv_test.run_test()
            Python_4200.K4200_test.last_test = "iv"

        elif self.cv_tabs.visible:
            self.cv_test.run_test()
            Python_4200.K4200_test.last_test = "c"

        elif self.cf_tabs.visible:
            self.cf_test.run_test()
            Python_4200.K4200_test.last_test = "c"

        elif self.iv_tabs.visible:
            self.iv_test.run_test()
            Python_4200.K4200_test.last_test = "iv"

    def boot(self):
        """
        ------------------------------------------------------------------------
        FUNCTION: init_GUI
        INPUTS: test (Python_4200.test)
        RETURNS: none
        DEPENDENCIES: IPython.html.widgets, IPython.display.display
        ------------------------------------------------------------------------
        Takes all the packaged sliders and menus from other functions and puts
        them into a tab structure. Then adds titles and borders to each. The
        "Run Test" button is also created here, although is hidden if the
        off-line mode flag is set to prevent a program crash when not connected
        to test set-up.
        ------------------------------------------------------------------------
        """
        self.config_page = self.equipment_config()
        self.make_cf_tabs()
        self.make_cv_tabs()
        self.make_iv_tabs()
        vf_tabs = [self.cv_tabs, self.cf_tabs, self.iv_tabs]
        for tabs in vf_tabs:
            tabs.set_title(1, 'Wavelength Range')
            tabs.set_title(2, 'Timings')
            tabs.set_title(3, 'Test Parameters')
            tabs.set_title(4, 'Equipment Configuration')
            tabs.set_title(5, 'Path')
        self.cv_tabs.visible = True
        self.cf_tabs.visible = False
        self.iv_tabs.visible = False
        self.top_bar()
