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
        from ltr559 import LTR559 #pip install ltr559
        import VL53L1X # pip install VL53L1X, REQUIRED: smbus2
        self.LTR559 = LTR559
        self.VL53L1X = VL53L1X

        pass
    def get_distance_from_object(self,range:int = 1, bus: int = 1,address:int = 0x29,timing:int = 0) -> int:
        #Docs: https://github.com/pimoroni/vl53l1x-python
        tof = self.VL53L1X.VL53L1X(i2c_bus=bus, i2c_address=address)
        tof.open()
        if timing != 0:
            tof.set_timing(66000, timing)
            tof.start_ranging(0)  # Start ranging
        else:
            tof.start_ranging(range) # 0 = Unchanged, 1 = Short Range, 2 = Medium Range, 3 = Long Range
        distance = tof.get_distance() #mm
        tof.stop_ranging()  # Stop ranging
        tof.close()
        if distance < 50: #acurate until 40mm +-25%
            return distance
        else:
            return distance
    def focus_roi(self,range:int = 1, bus: int = 1,address:int = 0x29,type:str = "w") -> int:
        tof = self.VL53L1X.VL53L1X(i2c_bus=bus, i2c_address=address)
        tof.open()
        if type == "w":
            # Wide scan forward ~30deg angle
            roi = self.VL53L1X.VL53L1xUserRoi(0, 15, 15, 0)
        elif type == "c":
            # Focused scan forward
            roi = self.VL53L1X.VL53L1xUserRoi(6, 9, 9, 6)
        elif type == "t":
            # Focused scan top
            roi = self.VL53L1X.VL53L1xUserRoi(6, 15, 9, 12)
        elif type == "b":
            # Focused scan bottom
            roi = self.VL53L1X.VL53L1xUserRoi(6, 3, 9, 0)
        elif type == "l":
            # Focused scan left
            roi = self.VL53L1X.VL53L1xUserRoi(0, 9, 3, 6)
        elif type == "r":
            # Focused scan right
            roi = self.VL53L1X.VL53L1xUserRoi(12, 9, 15, 6)
        else:
            print("Scan: wide (default)")
            roi = self.VL53L1X.VL53L1xUserRoi(0, 15, 15, 0)
        tof.set_user_roi(roi)
        tof.start_ranging(range) # 0 = Unchanged, 1 = Short Range, 2 = Medium Range, 3 = Long Range
        distance = tof.get_distance() #mm
        tof.stop_ranging()  # Stop ranging
        tof.close()
        if distance < 50: #acurate until 40mm +-25%
            return distance
        else:
            return distance
    def change_address_tof(self,current_address: int = 0x29, new_address: int = 0x29, bus: int = 1) -> None:
        tof = self.VL53L1X.VL53L1X(i2c_bus=bus, i2c_address=current_address)
        tof.open()
        if new_address is not current_address:
            tof.change_address(new_address)
        tof.close()

    def get_ambient_light(self) -> int:
        #Docs: https://github.com/pimoroni/ltr559-python
        ltr559 = self.LTR559()
        ltr559.update_sensor()
        lux = ltr559.get_lux()
        return lux

    def get_proximity(self):
        ltr559 = self.LTR559()
        ltr559.update_sensor()
        prox = ltr559.get_proximity()
        return prox
    
class HW():
    def __init__(self) -> None:
        import RPi.GPIO as GPIO
        self.GPIO = GPIO

        self.pwm_freq = 1000 #PWM frequency
        self.GPIO.setmode(self.GPIO.BOARD)
        self.GPIO.setup(self.led_pin, self.GPIO.OUT)
        self.pwm = self.GPIO.PWM(self.led_pin, self.pwm_freq)
        self.led_pin = 12 #LED Driver pwm pin

        with open(os.path.dirname(__file__) + '/../config.json') as json_file: #load config.json
            self.config = json.load(json_file)

    def set_brightness(self,start,end,direction,increment):
        self.pwm.start(1)
        for cycle in range(start, end, direction):
            self.pwm_freq = int(cycle / 100 * 65535)
            self.pwm.ChangeDutyCycle = self.pwm_freq

            time.sleep(0.25 / increment)
        self.pwm.stop()
        self.GPIO.cleanup()
    def get_brightness(self):
        return (int(self.pwm_freq)/65535)*100