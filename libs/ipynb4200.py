import serial
from IPython.html import widgets
from IPython.display import display


def init_GUI(cv_tests):
    ports = ['COM' + str(i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    vstep_slider = widgets.FloatSlider(min=0.1, max=2, step=0.1, value=1)
    vstart_slider = widgets.IntSlider(min=-30, max=30, value=0)
    vend_slider = widgets.IntSlider(min=-30, max=30, value=5)

    wstep_slider = widgets.IntSlider(min=50, max=500, step=50, value=250)
    wstart_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5000)
    wend_slider = widgets.IntSlider(min=3000, max=8000, step=100, value=5500)

    start_button = widgets.Button(description="Run test")

    mono_com_select = widgets.Dropdown(
        options=result,
        description="Monochromator port")

    ard_com_select = widgets.Dropdown(
        options=result,
        description="Arduino Shutter port",
        value="COM12")

    length_menu = widgets.Dropdown(
        options=["0", "1.5", "3"],
        description="Cable Length",
        value="1.5")

    single_w = widgets.Checkbox(
        description="Single Wavelength:",
        value=False)

    single_w_slider = widgets.IntSlider(
        description="Wavelength",
        min=300,
        max=8000,
        step=100,
        value=5500)

    def sw(x):
        cv_tests[0].single_w_val = x

    def sl(l):
        cv_tests[0].length = l

    def mono_com(c):
        cv_tests[0].mono = c
        print(cv_tests[0].mono)

    def ard_com(a):
        cv_tests[0].shut = a

    vstep_slider.description = "Voltage Step"
    vstart_slider.description = "Start Voltage"
    vend_slider.description = "End Voltage "

    wstep_slider.description = "Wavelength Step"
    wstart_slider.description = "Start Wavelength"
    wend_slider.description = "End Wavelength"

    v1 = widgets.interactive(
        cv_tests[0].set_vrange,
        vstart=vstart_slider,
        vend=vend_slider,
        vstep=vstep_slider)

    w1 = widgets.interactive(
        cv_tests[0].set_wavelengths,
        wstart=wstart_slider,
        wend=wend_slider,
        wstep=wstep_slider)

    w2 = widgets.interactive(
        sw,
        x=single_w_slider)

    l1 = widgets.interactive(sl, l=length_menu)
    c1 = widgets.interactive(mono_com, c=mono_com_select)
    s1 = widgets.interactive(ard_com, a=ard_com_select)

    page1 = widgets.Box(children=[v1])
    page2 = widgets.Box(children=[single_w, w1, w2])
    page3 = widgets.VBox(
        children=[length_menu, mono_com_select, ard_com_select])
    page3.border_width = 20
    page3.border_color = "white"

    tabs = widgets.Tab(children=[page1, page2, page3])

    display(tabs)
    display(start_button)
    tabs.set_title(0, 'Voltage Range')
    tabs.set_title(1, 'Wavelength Range')
    tabs.set_title(2, 'Equipment Configuration')

    w1.visible = True
    w2.visible = False

    def one_or_many(name, value):
        if value:
            w1.visible = False
            w2.visible = True
            cv_tests[0].wrange_set = False

        else:
            w1.visible = True
            w2.visible = False
            cv_tests[0].wrange_set = True

    started = False

    def start_test(name):
        if not started:
            cv_tests[0].test_setup = False
            cv_tests[0].run_test()

    single_w.on_trait_change(one_or_many, 'value')
    start_button.on_click(start_test)
