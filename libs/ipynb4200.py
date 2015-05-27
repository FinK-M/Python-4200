import serial
from IPython.html import widgets
from IPython.display import display


def v_sliders(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: v_sliders
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS: widgets.Box
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Generates three sliders for the selection of start/end voltages, and
    voltage step. Adds a description to each then packages them in a box widget
    which is then returned.
    ---------------------------------------------------------------------------
    """

    vstep_slider = widgets.FloatSlider(min=0.1, max=2, step=0.1, value=1)
    vstart_slider = widgets.IntSlider(min=-30, max=30, value=0)
    vend_slider = widgets.IntSlider(min=-30, max=30, value=5)

    vstep_slider.description = "Voltage Step"
    vstart_slider.description = "Start Voltage"
    vend_slider.description = "End Voltage "

    voltage_sliders = widgets.interactive(
        cv_test.set_vrange,
        vstart=vstart_slider,
        vend=vend_slider,
        vstep=vstep_slider)

    return widgets.Box(children=[voltage_sliders],
                       height=200)


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


def delays(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: delays
    INPUTS: cv_test (Python_4200.cv_test)
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
    minute_delay_slider = widgets.IntSlider(min=0, max=60, step=1, value=0)
    second_delay_slider = widgets.IntSlider(min=0, max=60, step=1, value=0)

    minute_wait_slider.description = "Minutes"
    second_wait_slider.description = "Seconds"
    minute_delay_slider.description = "Minutes"
    second_delay_slider.description = "Seconds"

    wait_text = widgets.HTML(
        value="Select time in minutes and seconds that " +
        "shutter closes for between voltage sweeps")
    wait_text.border_width = 10
    wait_text.border_color = "white"

    delay_text = widgets.HTML(
        value="Select time delay between each voltage level in each sweep")
    delay_text.border_width = 10
    delay_text.border_color = "white"

    set_minute_wait = widgets.interactive(
        cv_test.set_minute_wait,
        t=minute_wait_slider)

    set_second_wait = widgets.interactive(
        cv_test.set_second_wait,
        t=second_wait_slider)

    set_minute_delay = widgets.interactive(
        cv_test.set_minute_delay,
        t=minute_delay_slider)

    set_second_delay = widgets.interactive(
        cv_test.set_second_delay,
        t=second_delay_slider)

    return widgets.Box(children=[wait_text, set_minute_wait,
                                 set_second_wait, delay_text,
                                 set_minute_delay, set_second_delay])


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
    if len(result) == 0:
        result.append("No Ports")
        default = "No Ports"
        offline_mode = True
    elif "COM12" in result:
        default = "COM12"
    elif "COM13" in result:
        default = "COM13"
    else:
        default = "COM1"

    return offline_mode, result, default


def com_selectors(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: com_selectors
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
             offline_mode (bool)
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Takes the available COM ports generated by the com_discovery function and
    puts them into two drop down menu widgets, returns these two widgets, and
    forwards the off-line mode variable.
    ---------------------------------------------------------------------------
    """
    offline_mode, result, default = com_discovery()

    mono_com_select = widgets.Dropdown(
        options=result,
        description="Monochromator port")

    ard_com_select = widgets.Dropdown(
        options=result,
        description="Arduino Shutter port",
        value=default)

    mono_port_set = widgets.interactive(
        cv_test.set_mono_port,
        p=mono_com_select)

    shutter_port_set = widgets.interactive(
        cv_test.set_shutter_port,
        p=ard_com_select)

    return mono_port_set, shutter_port_set, offline_mode


def equipment_config(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: equipment_config
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS: mono_port_set, shutter_port_set (widgets.interactive)
             offline_mode (bool)
    DEPENDENCIES: IPython.html.widgets
    ---------------------------------------------------------------------------
    Takes the two COM port drop down menus, and adds them to a VBox widget
    along with a length select drop down. Formats the Vbox to centre the menus
    and adds a white border. Then returns this Vbox
    ---------------------------------------------------------------------------
    """
    mono_port_set, shutter_port_set, offline_mode = com_selectors(cv_test)

    length_menu = widgets.Dropdown(
        options=["0", "1.5", "3"],
        description="Cable Length",
        value="1.5")

    length_set = widgets.interactive(
        cv_test.set_length,
        length=length_menu)

    menu_wrapper = widgets.VBox(children=[
        length_set, mono_port_set, shutter_port_set])

    menu_wrapper.align = "end"
    menu_wrapper.width = 400
    menu_wrapper.border_width = 20
    menu_wrapper.border_color = "white"

    return widgets.VBox(children=[menu_wrapper],
                        height=200), offline_mode


def test_params(cv_test):

    frequencies = ['1K', '2K', '3K', '4K', '5K', '6K', '7K', '8K', '9K',
                   '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K',
                   '90K', '100K', '200K', '300K', '400K', '500K', '600K',
                   '700K', '800K', '900K', '1M', '2M', '3M', '4M', '5M', '6M',
                   '7M', '8M', '9M', '10M']

    acv_slider = widgets.IntSlider(min=10, max=100, step=1, value=30)
    acv_slider.description = "AC ripple voltage (mV)"
    acv_set = widgets.interactive(cv_test.set_acv, acv=acv_slider)
    acv_set.border_width = 10
    acv_set.border_color = "white"

    freq_select = widgets.Dropdown(options=frequencies, value="1M")
    freq_select.description = "AC ripple frequency"
    freq_set = widgets.interactive(cv_test.set_freq, freq=freq_select)
    freq_set.border_width = 10
    freq_set.border_color = "white"

    open_comp = widgets.Checkbox(
        description="Open",
        value=False)

    short_comp = widgets.Checkbox(
        description="Short",
        value=False)

    load_comp = widgets.Checkbox(
        description="Load",
        value=False)

    set_open = widgets.interactive(cv_test.set_open, o=open_comp)
    set_short = widgets.interactive(cv_test.set_short, s=short_comp)
    set_load = widgets.interactive(cv_test.set_load, l=load_comp)

    comp_description = widgets.HTML(value="Select test compensations")
    comps = widgets.HBox(children=[set_open, set_short, set_load])

    comp_box = widgets.VBox(children=[comp_description, comps])
    comp_box.border_width = 10
    comp_box.border_color = "white"
    comp_box.align = "center"

    return widgets.VBox(children=[acv_set, freq_set, comp_box],
                        height=1000)


def init_GUI(cv_test):
    """
    ---------------------------------------------------------------------------
    FUNCTION: init_GUI
    INPUTS: cv_test (Python_4200.cv_test)
    RETURNS: none
    DEPENDENCIES: IPython.html.widgets, IPython.display.display
    ---------------------------------------------------------------------------
    Takes all the packaged sliders and menus from other functions and puts them
    into a tab structure. Then adds titles and borders to each. The "Run Test"
    button is also created here, although is hidden if the off-line mode flag
    is set to prevent a program crash when not connected to test set-up.
    ---------------------------------------------------------------------------
    """
    page1 = v_sliders(cv_test)
    page2 = w_sliders(cv_test)
    page3 = delays(cv_test)
    page4 = test_params(cv_test)
    page5, offline_mode = equipment_config(cv_test)

    pages = [page1, page2, page3, page4, page5]
    for page in pages:
        page.border_width = 20
        page.border_color = "white"
        page.align = "center"

    tabs = widgets.Tab(children=pages)
    tabs.set_title(0, 'Voltage Range')
    tabs.set_title(1, 'Wavelength Range')
    tabs.set_title(2, 'Timings')
    tabs.set_title(3, 'Test Parameters')
    tabs.set_title(4, 'Equipment Configuration')

    display(tabs)

    def start_test(name):
        cv_test.test_setup = False
        cv_test.run_test()

    if not offline_mode:
        start_button = widgets.Button(description="Run test")
        display(start_button)
        start_button.on_click(start_test)
