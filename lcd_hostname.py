#! /usr/bin/env python

import sys
import socket
sys.path.insert(1, '/home/pi/lcd')
import drivers

display = drivers.Lcd()

display.lcd_display_string("Hostname:", 1) # Write line of text to first line of display
display.lcd_display_string(socket.gethostname(), 2) # Write line of text to second line of display
