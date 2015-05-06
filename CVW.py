from libs import Python_4200

test = Python_4200.cv_test("test", delay=0.5, mono="COM1", wait=1, length=3)
test.set_vrange(0, 5, 1)
test.set_wavelengths(4000, 6000, 250)
test.run_test()
