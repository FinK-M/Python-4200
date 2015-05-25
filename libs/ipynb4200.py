import serial
from IPython.html import widgets
from IPython.display import display


def init_GUI(cv_test):
    ports = ['COM' + str(i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    if "COM12" in result:
        default = "COM12"
    elif "COM13" in result:
        default = "COM13"
    else:
        default = "COM1"

    vstep_slider = widgets.FloatSlider(min=0.1, max=2, step=0.1, value=1)
    vstart_slider = widgets.IntSlider(min=-30, max=30, value=0)
    vend_slider = widgets.IntSlider(min=-30, max=30, value=5)

    wstep_slider = widgets.IntSlider(min=50, max=500, step=50, value=250)
    wstart_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5000)
    wend_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5500)

    vstep_slider.description = "Voltage Step"
    vstart_slider.description = "Start Voltage"
    vend_slider.description = "End Voltage "

    wstep_slider.description = "Wavelength Step"
    wstart_slider.description = "Start Wavelength"
    wend_slider.description = "End Wavelength"

    mono_com_select = widgets.Dropdown(
        options=result,
        description="Monochromator port")

    ard_com_select = widgets.Dropdown(
        options=result,
        description="Arduino Shutter port",
        value=default)

    length_menu = widgets.Dropdown(
        options=["0", "1.5", "3"],
        description="Cable Length",
        value="1.5")

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

    single_w = widgets.Checkbox(
        description="Single Wavelength:",
        value=False)

    single_w_slider = widgets.IntSlider(
        description="Wavelength",
        min=300,
        max=8000,
        step=100,
        value=5500)

    voltage_sliders = widgets.interactive(
        cv_test.set_vrange,
        vstart=vstart_slider,
        vend=vend_slider,
        vstep=vstep_slider)

    wavelength_sliders = widgets.interactive(
        cv_test.set_wavelengths,
        wstart=wstart_slider,
        wend=wend_slider,
        wstep=wstep_slider)

    length_set = widgets.interactive(
        cv_test.set_length,
        length=length_menu)

    mono_port_set = widgets.interactive(
        cv_test.set_mono_port,
        p=mono_com_select)

    shutter_port_set = widgets.interactive(
        cv_test.set_shutter_port,
        p=ard_com_select)

    single_wavelength_set = widgets.interactive(
        cv_test.set_single_w,
        w=single_w_slider)

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

    menu_wrapper = widgets.VBox(children=[
        length_set, mono_port_set, shutter_port_set])

    menu_wrapper.align = "end"
    menu_wrapper.width = 400
    menu_wrapper.border_width = 20
    menu_wrapper.border_color = "white"

    page1 = widgets.Box(children=[voltage_sliders],
                        height=200)

    page2 = widgets.Box(children=[single_w, wavelength_sliders,
                                  single_wavelength_set],
                        height=200)

    page3 = widgets.Box(children=[wait_text, set_minute_wait,
                                  set_second_wait, delay_text,
                                  set_minute_delay, set_second_delay])

    page4 = widgets.VBox(children=[menu_wrapper],
                         height=200)

    pages = [page1, page2, page3, page4]
    for page in pages:
        page.border_width = 20
        page.border_color = "white"

    tabs = widgets.Tab(children=pages)
    tabs.set_title(0, 'Voltage Range')
    tabs.set_title(1, 'Wavelength Range')
    tabs.set_title(2, 'Timings')
    tabs.set_title(3, 'Equipment Configuration')

    display(tabs)

    start_button = widgets.Button(description="Run test")
    display(start_button)

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

    started = False

    def start_test(name):
        if not started:
            cv_test.test_setup = False
            cv_test.run_test()

    single_w.on_trait_change(one_or_many, 'value')
    start_button.on_click(start_test)
