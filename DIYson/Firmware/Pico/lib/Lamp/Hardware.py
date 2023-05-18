"""
MIT License
Copyright (c) 2023 Joseph0M

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import random
import datetime
import math
import json
import os.path
class Sensor():
    def __init__(self) -> None:
        from pimoroni_circuitpython_ltr559 import Pimoroni_LTR559 # REQUIRED: Adafruit Register, pimoroni-circuitpython-ltr559
        import adafruit_vl53l1x # REQUIRED: Adafruit PlatformDetect, Adafruit Blinka, adafruit-circuitpython-vl53l1x
        import board
        import busio
        self.LTR559 = Pimoroni_LTR559
        self.VL53L1X = adafruit_vl53l1x
        self.board = board
        self.busio = busio

        pass
    def get_distance_from_object(self,range:int = 1,timing:int = 0) -> int:
        #Docs: https://learn.adafruit.com/adafruit-vl53l1x/python-circuitpython , https://github.com/adafruit/Adafruit_CircuitPython_VL53L1X
        i2c = self.busio.I2C(self.board.GP17, self.board.GP16)
        # i2c = self.board.STEMMA_I2C()  # For using the built-in STEMMA QT connector
        vl53 = self.VL53L1X.VL53L1X(i2c)
        vl53.distance_mode = range
        if timing == 0:
            vl53.timing_budget = 100
        else:
            vl53.timing_budget = timing
        model_id, module_type, mask_rev = vl53.model_info
        vl53.start_ranging()
        if vl53.data_ready:
            vl53.clear_interrupt()
            vl53.stop_ranging()
            if vl53.distance == None:
                return 0
            return vl53.distance
        else:
            vl53.stop_ranging()
            return 0
    def focus_roi(self,range:int = 1, bus: int = 1,address:int = 0x29,type:str = "w"):
        #NOT SUPPORTED ON RP2040
        return 0

    def get_ambient_light(self) -> int:
        #Docs: https://github.com/pimoroni/ltr559-python
        i2c = self.busio.I2C(self.board.GP17, self.board.GP16)
        LTR559 = self.LTR559(i2c)
        return LTR559.lux
    def get_proximity(self) -> int:
        i2c = self.busio.I2C(self.board.GP17, self.board.GP16)
        LTR559 = self.LTR559(i2c)
        return LTR559.prox
    
class HW():
    def __init__(self) -> None:
        from machine import Pin, PWM, I2C
        self.PWM = PWM
        self.Pin = Pin
        self.pwm_freq = 1000
        self.led_pin = 15 #LED Driver pwm pin

        with open(os.path.dirname(__file__) + '/../config.json') as json_file: #load config.json
            self.config = json.load(json_file)

    def set_brightness(self,start,end,direction,increment):
        pwm = self.PWM(self.Pin(self.led_pin))
        pwm.freq(self.pwm_freq)
        for cycle in range(start, end, direction):
            pwm.duty_cycle = int(cycle / 100 * 65535)
            time.sleep(0.25 / increment)
    def get_brightness(self):
        pwm = self.PWM(self.Pin(self.led_pin))
        pwm.freq(self.pwm_freq)
        return (int(pwm.duty_cycle)/65535)*100
    