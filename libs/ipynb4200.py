import serial
from IPython.html import widgets
from IPython.display import display
import threading
from datetime import datetime
from libs import Python_4200
from time import sleep


def test_update(test, **kwargs):
    for name, value in kwargs.items():
        setattr(test, name, value)


def cap_test_update(**kwargs):
    for name, value in kwargs.items():
        setattr(Python_4200.cap_test, name, value)


def K4200_class_update(**kwargs):
    for name, value in kwargs.items():
        setattr(Python_4200.K4200_test, name, value)


def v_sliders(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: v_sliders
    INPUTS: test (Python_4200.test)
    RETURNS: widgets.Box
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Generates three sliders for the selection of start/end voltages, and
    voltage step. Adds a description to each then packages them in a box widget
    which is then returned.
    ---------------------------------------------------------------------------
    """
    if test.mode in ("cv", "cf"):
        vstep_select = widgets.FloatSlider(min=0.1, max=2, step=0.1, value=1)
        vstart_select = widgets.IntSlider(min=-30, max=30, value=0)
        vend_select = widgets.IntSlider(min=-30, max=30, value=5)
    elif test.mode == "iv":
        vstep_select = widgets.BoundedFloatText(min=0.01, max=10, value=1)
        vstart_select = widgets.BoundedIntText(min=-30, max=30, value=0)
        vend_select = widgets.BoundedIntText(min=-30, max=30, value=5)
        vstep_select.margin = 10
        vstart_select.margin = 10
        vend_select.margin = 10
        description = widgets.HTML(value="""
        <h3>SMU Voltage sweep configuration</h3>
        <p>Start and end voltages can be between -210.00V and 210.00V.</p>
        <p>Step voltage can also be anywhere in this range, although should
        be less than half the overall voltage range.</p>
        """)

    vstep_select.description = "Step"
    vstart_select.description = "Start"
    vend_select.description = "End"

    voltage_select = widgets.interactive(
        test.set_vrange,
        vstart=vstart_select,
        vend=vend_select,
        vstep=vstep_select)
    if test.mode in ("cv", "cf"):
        return widgets.Box(children=[voltage_select],
                           height=200)
    else:
        selectors = widgets.VBox(
            children=[vstart_select, vstep_select, vend_select],
            align="start")
        return widgets.HBox(children=[selectors, description])


def w_sliders(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: w_sliders
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS: widgets.Box
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Generates four sliders for the selection of start/end wavelengths,
    wavelength step, and single wavelength. Adds a description to each. Also
    creates a single or many wavelength selector with corresponding function to
    hide sliders. Tick box and all sliders are packaged in a widget box and
    returned
    ---------------------------------------------------------------------------
    """

    wstep_slider = widgets.IntSlider(min=50, max=500, step=50, value=250)
    wstart_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5000)
    wend_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5500)

    wstep_slider.description = "Wavelength Step"
    wstart_slider.description = "Start Wavelength"
    wend_slider.description = "End Wavelength"

    wavelength_sliders = widgets.interactive(
        cv_test.set_wavelengths,
        wstart=wstart_slider,
        wend=wend_slider,
        wstep=wstep_slider)

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
        cv_test.set_single_w,
        w=single_w_slider)

    wavelength_sliders.visible = True
    single_wavelength_set.visible = False

    def one_or_many(name, value):
        if value:
            wavelength_sliders.visible = False
            single_wavelength_set.visible = True
            cv_test.wrange_set = False

        else:
            wavelength_sliders.visible = True
            single_wavelength_set.visible = False
            cv_test.wrange_set = True

    single_w.on_trait_change(one_or_many, 'value')

    return widgets.Box(children=[single_w, wavelength_sliders,
                                 single_wavelength_set],
                       height=200)


def delays(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: delays
    INPUTS: test (Python_4200.test)
    RETURNS: widgets.Box
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Generates four sliders for the selection of shutter and sweep delays and
    adds a description to each. Also creates two HTML widgets to provide a
    small subtitle to explain the purpose of the two pairs of sliders.
    ---------------------------------------------------------------------------
    """
    minute_wait_slider = widgets.IntSlider(min=0, max=60, step=1, value=0)
    second_wait_slider = widgets.IntSlider(min=0, max=60, step=1, value=0)
    delay_slider = widgets.IntSlider(min=0, max=60, step=1, value=0)

    minute_wait_slider.description = "Minutes"
    second_wait_slider.description = "Seconds"
    delay_slider.description = "Seconds"

    wait_text = widgets.HTML(
        value="Select time in minutes and seconds that " +
        "shutter closes for between voltage sweeps")
    wait_text.border_width = 10
    wait_text.border_color = "white"

    delay_text = widgets.HTML(
        value="Select time delay between each voltage level in each sweep")
    delay_text.border_width = 10
    delay_text.border_color = "white"

    set_delay = widgets.interactive(
        test.set_delay,
        delay=delay_slider)

    set_wait = widgets.interactive(
        test.set_wait,
        wait_sec=second_wait_slider,
        wait_min=minute_wait_slider)

    return widgets.Box(children=[wait_text, set_wait, delay_text, set_delay])


def visa_selector():
    resources = Python_4200.K4200_test.rm.list_resources()
    if len(resources) == 0:
        visa_okay = False
        result = ["No resources"]
    else:
        visa_okay = True
        result = [r for r in resources if "ASRL" not in r]

    K4200_select = widgets.Dropdown(
        options=result,
        description="4200 SCS address")
    if "GPIB0::17::INSTR" in result:
        K4200_select.value = "GPIB0::17::INSTR"
    K4200_select.margin = 5

    LS331_select = widgets.Dropdown(
        options=result,
        description="LS 331 address")
    if "GPIB0::1::INSTR" in result:
        LS331_select.value = "GPIB0::1::INSTR"
    LS331_select.margin = 5

    if visa_okay:
        widgets.interactive(
            K4200_class_update,
            k4200_address=K4200_select,
            ls331_address=LS331_select)
        visa_select = widgets.VBox(children=[K4200_select, LS331_select])
        visa_select.align = "end"
        visa_select.margin = 10
    return visa_okay, visa_select


def com_discovery():
    """
    ---------------------------------------------------------------------------
    FUNCTION: com_discovery
    INPUTS: None
    RETURNS: offline_mode (bool)
             result, default (str)
    DEPENDENCIES: serial
    ---------------------------------------------------------------------------
    Generates a list of all possible windows COM ports then generates a list of
    which ones are available. Also takes a guess as to which one the Arduino
    shutter is connected to (usually higher number ports). If none are
    available sets the "off-line mode" flag so GUI can still run on other PCs
    ---------------------------------------------------------------------------
    """
    ports = ['COM' + str(i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    com_okay = True
    if len(result) == 0:
        result.append("No Ports")
        default = "No Ports"
        com_okay = False
    elif "COM12" in result:
        default = "COM12"
    elif "COM13" in result:
        default = "COM13"
    else:
        default = "COM1"

    return com_okay, result, default


def com_selectors():
    """
    ---------------------------------------------------------------------------
    FUNCTION: com_selectors
    INPUTS: test (Python_4200.test)
    RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
             offline_mode (bool)
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Takes the available COM ports generated by the com_discovery function and
    puts them into two drop down menu widgets, returns these two widgets, and
    forwards the off-line mode variable.
    ---------------------------------------------------------------------------
    """
    com_okay, result, default = com_discovery()

    mono_com_select = widgets.Dropdown(
        options=result,
        description="Monochromator port")
    mono_com_select.margin = 5

    ard_com_select = widgets.Dropdown(
        options=result,
        description="Arduino Shutter port",
        value=default)
    ard_com_select.margin = 5
    K4200_class_update(
        mono_port="COM1",
        shutter_port=default)
    widgets.interactive(
        K4200_class_update,
        mono_port=mono_com_select,
        shutter_port=ard_com_select)

    com_select = widgets.VBox(children=[mono_com_select, ard_com_select])
    com_select.align = "end"
    com_select.margin = 10

    return com_select, com_okay


def equipment_config():
    """
    ---------------------------------------------------------------------------
    FUNCTION: equipment_config
    INPUTS: None
    RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
             offline_mode (bool)
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Takes the two COM port drop down menus, and adds them to a VBox widget
    along with a length select drop down. Formats the Vbox to centre the menus
    and adds a white border. Then returns this Vbox
    ---------------------------------------------------------------------------
    """
    left_wrapper, com_okay = com_selectors()
    visa_okay, right_wrapper = visa_selector()
    offline_mode = not (com_okay and visa_okay)

    menu_wrapper = widgets.HBox(children=[left_wrapper, right_wrapper])
    menu_wrapper.align = "center"

    return widgets.VBox(children=[menu_wrapper],
                        height=200), offline_mode


def ac_volt(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    acv_slider = widgets.IntSlider(min=10, max=100, step=1, value=30)
    acv_slider.description = "AC ripple voltage (mV)"
    acv_slider.margin = 10

    widgets.interactive(cv_test.set_acv, acv=acv_slider)

    return acv_slider


def ac_range(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    acz_range = widgets.Dropdown(
        options={"Auto": "0", "1µA": "1E-6", "30µA": "30E-6", "1mA": "1E-3"},
        value="0")
    acz_range.align = "end"
    acz_range.description = "Current Range"
    acz_range.margin = 5

    widgets.interactive(cv_test.set_acz, acz=acz_range)

    return acz_range


def ac_freq(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: test (Python_4200.test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    one_to_ten = [str(i) for i in range(1, 11)]
    order = {"1K": 1000, "10K": 10000, "100K": 100000, "1M": 1000000}

    freq_num = widgets.Dropdown(options=one_to_ten, value="1")
    freq_num.description = "AC Start Frequency"
    freq_num.margin = 5

    freq_order = widgets.Dropdown(options=order, value=1000000)
    freq_order.description = "Order"
    freq_order.margin = 5

    if test.mode == "cv":
        widgets.interactive(
            test.set_freq,
            f_num=freq_num,
            f_order=freq_order)
        return freq_num, freq_order
    elif test.mode == "cf":

        freq_num2 = widgets.Dropdown(options=one_to_ten, value="3")
        freq_num2.description = "AC End Frequency"
        freq_num2.margin = 5

        freq_order2 = widgets.Dropdown(options=order, value=1000000)
        freq_order2.description = "Order"
        freq_order2.margin = 5

        widgets.interactive(
            test.set_frange,
            fstart_num=freq_num,
            fstart_ord=freq_order,
            fend_num=freq_num2,
            fend_ord=freq_order2)

        freq_nums = widgets.VBox(children=[freq_num, freq_num2])
        freq_nums.align = "end"
        freq_ords = widgets.VBox(children=[freq_order2, freq_order2])
        freq_ords.align = "end"
        return widgets.HBox(children=[freq_nums, freq_ords])


def speed(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: test (Python_4200.test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    speed_menu = widgets.Dropdown(
        options={"Fast": 0, "Normal": 1, "Quiet": 2},
        value=1)
    speed_menu.description = "Integration speed"
    speed_menu.align = "end"
    speed_menu.margin = 5

    widgets.interactive(test.set_speed, speed=speed_menu)

    return speed_menu


def comps(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
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

    comps = widgets.HBox(children=[open_comp, short_comp, load_comp])
    comps.width = 290
    comps.border_color = "white"

    set_comps = widgets.interactive(
        cv_test.set_comps,
        open=open_comp,
        short=short_comp,
        load=load_comp)
    set_comps.border_color = "white"
    set_comps.border_width = 10

    comp_description = widgets.HTML(value="Select test compensations")

    comp_box = widgets.VBox(children=[comp_description, comps])
    comp_box.margin = 20
    comp_box.border_color = "white"
    comp_box.align = "center"

    return comp_box


def repeat_select(test):
    one_to_ten = [str(i) for i in range(1, 11)]
    repeat_menu = widgets.Dropdown(
        options=one_to_ten,
        value="3",
        description="Repetitions")
    repeat_menu.margin = 5
    widgets.interactive(
        test.set_repetitions,
        repetitions=repeat_menu)
    return repeat_menu


def iv_test_params(test):
    compliance_select = widgets.BoundedFloatText(min=(-105), max=105)
    sig_fig_select = widgets.IntSlider(min=3, max=7, value=5)
    widgets.interactive(
        test.set_compliance,
        compliance=compliance_select)
    widgets.interactive(
        test.set_sig_fig,
        sig_fig=sig_fig_select)
    compliance_text = widgets.HTML(value="""
    Enter current compliance between -105mA and 105mA""")
    order = ["E" + str(i) for i in range(-3, -13, -3)]
    min_cur_ord = widgets.Dropdown(options=order, value="E-3")
    min_cur_num = widgets.BoundedIntText(min=1, max=100)
    widgets.interactive(
        test.set_min_cur,
        num=min_cur_num,
        order=min_cur_ord)
    min_cur = widgets.HBox(children=[min_cur_num, min_cur_ord])
    compliance_select.margin = 10
    compliance_select.description = "mA"
    sig_fig_select.margin = 10
    sig_fig_select.description = "Significant Figures"
    min_cur_num.description = "Min Current"
    min_cur_ord.description = "Current Order"
    params = widgets.VBox(
        children=[compliance_text, compliance_select, sig_fig_select, min_cur])

    return params


def cap_test_params(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: test (Python_4200.test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """

    acz_range = ac_range(test)
    speed_menu = speed(test)
    comp_box = comps(test)
    acv_slider = ac_volt(test)

    length_menu = widgets.Dropdown(
        options=["0", "1.5", "3"],
        description="Cable Length",
        value="1.5")
    length_menu.margin = 5

    widgets.interactive(
        test.set_length,
        length=length_menu)

    repeat_menu = repeat_select(test)
    if test.mode == "cv":
        freq_num, freq_order = ac_freq(test)
        left_box = widgets.VBox(
            children=[freq_num, acz_range, length_menu],
            align="end",
            width=330)

        right_box = widgets.VBox(
            children=[freq_order, speed_menu, repeat_menu],
            align="end",
            width=330)
        box = widgets.HBox(children=[left_box, right_box])

    elif test.mode == "cf":
        left_box = widgets.VBox(
            children=[acz_range, length_menu],
            align="end",
            width=330)

        right_box = widgets.VBox(
            children=[speed_menu, repeat_menu],
            align="end",
            width=330)
        box = widgets.HBox(children=[left_box, right_box])
        box.align = "end"

    return widgets.VBox(children=[acv_slider, box, comp_box],
                        height=350)


def custom_name(test):
    """
    ---------------------------------------------------------------------------
    FUNCTION:
    INPUTS: test (Python_4200.test)
    RETURNS:
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    """
    descriptor = widgets.HTML(
        value="<p>Enter a custom description for the file/s produced by " +
        "this test.</p>" +
        "<p>Leave blank to just use automatically generated tags.</p>")
    descriptor.margin = 10
    name_input = widgets.Text(description="Custom Text")
    widgets.interactive(
        test.set_custom_name,
        name=name_input)

    time = widgets.HTML(value="")
    time.margin = 10

    def update():
        time.value = (
            "<b>Filename: </b>" + datetime.now().strftime("%H.%M.%S") +
            "_" + test.mode + test.cust_name + ".csv")
        threading.Timer(.5, update).start()
    update()

    return widgets.Box(children=[descriptor, name_input, time])


def boot_GUI():
    """
    ---------------------------------------------------------------------------
    FUNCTION: init_GUI
    INPUTS: test (Python_4200.test)
    RETURNS: none
    DEPENDENCIES: IPython.html.widgets, IPython.display.display
    ---------------------------------------------------------------------------
    Takes all the packaged sliders and menus from other functions and puts them
    into a tab structure. Then adds titles and borders to each. The "Run Test"
    button is also created here, although is hidden if the off-line mode flag
    is set to prevent a program crash when not connected to test set-up.
    ---------------------------------------------------------------------------
    """
    cv_test = Python_4200.cv_test("test")
    cf_test = Python_4200.cf_test("test")
    iv_test = Python_4200.iv_test("test")

    page5, offline_mode = equipment_config()
    cv_pages = [v_sliders(cv_test),
                w_sliders(cv_test),
                delays(cv_test),
                cap_test_params(cv_test),
                page5,
                custom_name(cv_test)]

    cf_pages = [ac_freq(cf_test),
                w_sliders(cf_test),
                delays(cf_test),
                cap_test_params(cf_test),
                page5,
                custom_name(cf_test)]

    iv_pages = [v_sliders(iv_test),
                w_sliders(iv_test),
                delays(iv_test),
                iv_test_params(iv_test),
                page5,
                custom_name(iv_test)]

    page_list = [cv_pages, cf_pages]
    for pages in page_list:
        for page in pages:
            page.border_width = 20
            page.border_color = "white"
            page.align = "center"
    for page in iv_pages:
        page.margin = 20

    cv_tabs = widgets.Tab(children=cv_pages)
    cv_tabs.description = ""
    cv_tabs.set_title(0, 'Voltage Range')

    cf_tabs = widgets.Tab(children=cf_pages)
    cf_tabs.description = ""
    cf_tabs.set_title(0, 'Frequency Range')

    iv_tabs = widgets.Tab(children=iv_pages)
    iv_tabs.description = ""
    iv_tabs.set_title(0, 'Voltage Range')

    vf_tabs = [cv_tabs, cf_tabs, iv_tabs]
    for tabs in vf_tabs:
        tabs.set_title(1, 'Wavelength Range')
        tabs.set_title(2, 'Timings')
        tabs.set_title(3, 'Test Parameters')
        tabs.set_title(4, 'Equipment Configuration')
        tabs.set_title(5, 'Path')
    cv_tabs.visible = True
    cf_tabs.visible = False
    iv_tabs.visible = False

    oneall_tick = widgets.Checkbox(
        description="Run All?")
    oneall_tick.margin = 20

    widgets.interactive(
        K4200_class_update,
        run_all=oneall_tick)

    select_types = widgets.ToggleButtons(
        options=["CV", "CF", "IV"],
        description="Test")
    select_types.margin = 20

    def visible_tabs(mode):
        if mode == "CV":
            cv_tabs.visible = True
            cf_tabs.visible = False
            iv_tabs.visible = False

        elif mode == "CF":
            cv_tabs.visible = False
            cf_tabs.visible = True
            iv_tabs.visible = False

        elif mode == "IV":
            cv_tabs.visible = False
            cf_tabs.visible = False
            iv_tabs.visible = True

    widgets.interactive(
        visible_tabs,
        mode=select_types)

    def start_test(name):
        if Python_4200.K4200_test.run_all:
            cv_test.run_test()
            Python_4200.K4200_test.last_test = "c"
            sleep(1)
            cf_test.run_test()
            Python_4200.K4200_test.last_test = "c"
            sleep(1)
            iv_test.run_test()
            Python_4200.K4200_test.last_test = "iv"
        elif cv_tabs.visible:
            cv_test.run_test()
            Python_4200.K4200_test.last_test = "c"
        elif cf_tabs.visible:
            cf_test.run_test()
            Python_4200.K4200_test.last_test = "c"
        elif iv_tabs.visible:
            iv_test.run_test()
            Python_4200.K4200_test.last_test = "iv"

    start_button = widgets.Button(description="Run test")
    start_button.on_click(start_test)
    start_button.margin = 20

    if not offline_mode:
        top = widgets.HBox(children=[select_types, oneall_tick, start_button])
        display(top, cv_tabs, cf_tabs, iv_tabs)
    else:
        display(select_types, cv_tabs, cf_tabs, iv_tabs)
