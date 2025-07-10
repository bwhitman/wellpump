# Tracking well pump power use of a Pentek Intellidrive PID10 controller

We have a well and during a retrofit to a whole-home backup battery, I wanted to know how much power the well was taking. 

The well has a controller with a screen but would only show instantaneous watts, and you had to be looking at the controller. I wanted to measure KW/h over time periods to size a battery setup.

The [well controller has a RS485 connection](https://www.pentair.com/content/dam/extranet/web/nam/pentek/manuals/pn957-pentek-intellidrive-pid-iom.pdf
). I hadn't ever done anything with RS485 so tried to wire up something to log the power use at small intervals. It was harder than I thought it would be, so I'm writing down my work here, to save the trouble of someone else in my same boat one day!

## Hardware setup

You have to have some way to convert RS485 to a form your MCU or computer can read. 

I at first wasted a lot of time trying to get a simpler [Sparkfun RS485 to serial breakout](https://www.sparkfun.com/sparkfun-transceiver-breakout-rs-485.html) working. That breakout uses a [SP3485](https://www.maxlinear.com/ds/sp3485.pdf
) chip. The problem with this chip is that it's half duplex -- you have to signal which direction you're reading / writing. This gets messy: on a Pi you have to set up the [RTS flow control](https://ethertubes.com/raspberry-pi-rts-cts-flow-control/
) and make a change to [the Python module that reads the serial port](https://github.com/pyhys/minimalmodbus/issues/137#issuecomment-2685900902
). On am MCU you have to set up some GPIO to toggle between read and write. 

Instead, I went simple and just used a Raspberry Pi and a [Waveshare USB to RS485 adapter.](https://www.waveshare.com/usb-to-rs485.htm) 

Get the Waveshare USB adapter instead. The downside is you need a computer, Pi, or MCU with USB host capability.

Wire the `A+` from the adapter to the `P` line on the well controller, and `B-` to `N`. I stripped two jumper wires (with an inch of length) and there's a plastic wire gripper on the well end. Seems stable. There's space on the bottom of the well controller for a Pi, it can close pretty neatly. A pro move would be to power the Pi from something inside the controller, but I left a USB C cable dangle through the access jack on the bottom.

Plug the adapter into the Pi's USB port.

## Software setup

Set up the Pi like normal. Install [minimalmodbus](https://minimalmodbus.readthedocs.io/en/stable/readme.html
) like `pip3 install minimalmodbus`. [Run this script](https://github.com/bwhitman/wellpump/blob/main/well.py) like `python3 well.py`. It will output a log file with a timestamp in milliseconds and the power of the pump in watts. 

TODO: have the script compute KWH from this log 


## Links, help

Some helpful links I found to bring this all together. 

https://devices.esphome.io/devices/Pentek-Intellidrive-PID10

https://terrylove.com/forums/index.php?threads/pentek-intellidrive-communications.99276/#post-730691

https://github.com/ryan-lang/pentek-intellidrive-modbus-docs/tree/main

