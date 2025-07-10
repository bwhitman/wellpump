import minimalmodbus, time
log = open("well_%d.log" % (int(time.time())), "w")
addrs = [5149] # watts
serialport = "/dev/ttyUSB0"
addr = 0x02
debug = False
fc = 3
instrument = minimalmodbus.Instrument(serialport,addr, debug=debug,  mode=minimalmodbus.MODE_RTU)
import time
while True:
    for i in addrs:
        t = instrument.read_long(i, number_of_registers=2, byteorder=minimalmodbus.BYTEORDER_BIG, signed=False, functioncode=fc)
        log.write("%d %d\n" % (int(time.time()*1000), t))
        log.flush()
        time.sleep(1.0)

