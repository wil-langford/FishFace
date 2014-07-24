#!/usr/bin/env python

"""
"""

import RPi.GPIO as gpio
import subprocess

__author__ = 'wil-langford'

gpio.setmode(gpio.BCM)
gpio.setup(25, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.wait_for_edge(25, gpio.FALLING)
subprocess.call(['/sbin/poweroff'])