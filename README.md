# Tracking well pump power use of a Pentek Intellidrive PID10 controller

We have a well, and during a retrofit to a whole-home backup battery, I wanted to know how much power the well was taking. 

The well has a controller with a screen but would only show instantaneous watts, and you had to be looking at the controller. I wanted to measure kWh over time periods to size a battery setup.

The [well controller has a RS485 connection](https://www.pentair.com/content/dam/extranet/web/nam/pentek/manuals/pn957-pentek-intellidrive-pid-iom.pdf
). I hadn't ever done anything with RS485 so I tried to wire up something to log the power use at intervals. It was harder than I thought it would be, so I'm writing down my work here, to save the trouble of someone else in my same boat one day!

## Hardware setup

You have to have some way to convert RS485 to a form your MCU or computer can read. The [SP3485](https://www.maxlinear.com/ds/sp3485.pdf) chip can help you convert from RS485 signal to a serial UART for your MCU or computer. 

However, RS485 (and thus the SP3485 on its own) [requires you to manage the direction of data manually.](https://www.seeedstudio.com/blog/2021/03/18/how-rs485-works-and-how-to-implement-rs485-into-industrial-control-systems/?srsltid=AfmBOopJcMqfHdq60BRMlKcLVJ6-GwC6fiv8oTCRtwjsQJ0RMf476MUE) I at first wasted a lot of time trying to get the simple [Sparkfun RS485 to serial breakout](https://www.sparkfun.com/sparkfun-transceiver-breakout-rs-485.html) working. You have to signal from your UART which direction -- reading or writing -- before each packet. This gets messy: on a Pi you have to wire RTS to a GPIO pin and then set up the [RTS flow control](https://ethertubes.com/raspberry-pi-rts-cts-flow-control/
) and lastly make a change to [the Python module that reads the serial port](https://github.com/pyhys/minimalmodbus/issues/137#issuecomment-2685900902
). On an MCU you'd have to set up a GPIO to toggle between read and write. I did eventually get this setup reading bytes, but had to mess with the timing of modbus responses, and it was very brittle. I do not recommend. 

Instead, I went simple and just used a Raspberry Pi and a [Waveshare USB to RS485 adapter.](https://www.waveshare.com/usb-to-rs485.htm) This adapter also uses the SP3485 but they have their own microcontroller that manages data direction from the UART. This makes it a lot easier to read and write RS485 data over a computer's (or Raspberry Pi etc) USB port. 

The Pentek pump controller uses [Modbus](https://en.wikipedia.org/wiki/Modbus) over RS485, at 19200 baud, accessible through two pins (`P` and `N`) on the external accessory rail. You can pull off the cover of the controller and you'll find the row of pins at the bottom. 

Wire the `A+` from the adapter to the `P` line on the well controller, and `B-` to `N`. I skipped connecting `GND` - I presume you could use the chassis, but leaving it unconnected had no negative impact for me. I stripped two jumper wires (with an inch of length) and there's a plastic wire gripper on the well end. Seems stable. There's space on the bottom of the well controller for a Pi, it can close pretty neatly. A pro move would be to power the Pi from something inside the controller, but I just left a USB C cable dangle through the access jack on the bottom.

Plug the adapter into the Pi's USB port.

## Software setup

Set up the Pi like normal. Install [minimalmodbus](https://minimalmodbus.readthedocs.io/en/stable/readme.html
) like `pip3 install minimalmodbus`. [Run this script](https://github.com/bwhitman/wellpump/blob/main/well.py) like `python3 well.py`. (I run mine in a `screen` and just keep it running all the time.) It will output a log file with a timestamp in milliseconds and the power of the pump in watts. 

To see kWh over hours or days, run [`python3 analyze.py`](https://github.com/bwhitman/wellpump/blob/main/analyze.py). It's a simple script to convert the watts per timeslice from the log to joules and then KW/H. Modify that to your needs!

We can also estimate gallons from kWh: we waited for the pump to report 0 watts, then flushed a toilet with a known fill size and divined gallons per kWh. This is a bit hand-wavy but for our use is generally on target. 

## Links, help

Some helpful links I found to bring this all together. 

 * [Someone got this going on ESPhome, which clued me into this being possible at all. But not a lot of setup documentation especially the hardware side.](https://devices.esphome.io/devices/Pentek-Intellidrive-PID10)
 * [I think the first person to reverse the RS485 bytes posted their work here.](https://terrylove.com/forums/index.php?threads/pentek-intellidrive-communications.99276/#post-730691)
 * [And then someone collated that work plus a response from Pentek with more detail on the data format](https://github.com/ryan-lang/pentek-intellidrive-modbus-docs/tree/main)

