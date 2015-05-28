from libs import Python_4200

test = Python_4200.cv_test("test", delay=0.1, mono="COM1", wait=1, length=3)
test.set_vrange(0, 2, 1)
test.set_wavelengths(4000, 5000, 500)
test.run_test()
