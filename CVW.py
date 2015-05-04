from libs import Python_4200

test = Python_4200.cv_test("test", delay=2, mono="COM1", wait=2)
test.set_vrange(2, 4, 1)
test.set_wavelengths(4500, 5500, 250)
test.run_test()
