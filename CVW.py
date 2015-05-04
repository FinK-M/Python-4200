from libs import Python_4200

test = Python_4200.cv_test("test", delay=0.1, mono="COM1")
test.set_vrange(-5,5,0.1)
test.set_wavelengths(3900,5000,100)
test.run_test()
