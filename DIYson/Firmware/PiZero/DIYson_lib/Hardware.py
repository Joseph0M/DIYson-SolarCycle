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
from .Serialization import serialize,deserialize,multi_function_serial
from .i2c import PI2PI_I2C

class Sensor():
    def __init__(self) -> None:
        import VL53L1X
        from ltr559 import LTR559
        self.VL53L1X = VL53L1X
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
        #self.tof = self.VL53L1X.VL53L1X(i2c_bus=int(self.config["SENSOR_DATA"]["TOF"]["I2C_BUS"]), i2c_address=0x29)
        self.als = LTR559()
        self.ps = self.als
    def get_distance_from_object(self,range:int = 1,timing:int = 33,focus:str="w") -> int:
        self.tof.open()
        self.tof.set_user_roi(self.focus_roi(focus))
        self.tof.start_ranging(range)
        distance = self.tof.get_distance()
        self.tof.stop_ranging()
        self.tof.close()
        return int(distance)
    
    def focus_roi(self,type:str = "w"):
        if type == "w":
            # Wide scan forward ~30deg angle
            return self.VL53L1X.VL53L1xUserRoi(0, 15, 15, 0)
        elif type == "c":
            #forward
            return self.VL53L1X.VL53L1xUserRoi(6, 9, 9, 6)
        elif type == "t":
            #top
            return self.VL53L1X.VL53L1xUserRoi(6, 15, 9, 12)
        elif type == "b":
            #bottom
            return self.VL53L1X.VL53L1xUserRoi(6, 3, 9, 0)
        elif type == "l":
            #eft
            return self.VL53L1X.VL53L1xUserRoi(0, 9, 3, 6)
        elif type == "r":
            #right
            return self.VL53L1X.VL53L1xUserRoi(12, 9, 15, 6)
        else:
            return self.VL53L1X.VL53L1xUserRoi(0, 15, 15, 0)

    def get_ambient_light(self) -> int:
        self.als.update_sensor()
        lux = self.als.get_lux()
        print(lux)
        return lux

    def get_proximity(self):
        self.ps.update_sensor()
        prox = self.ps.get_proximity()
        print(prox)
        return prox

class HW():
    def __init__(self) -> None:
        self.pi2pi = PI2PI_I2C(bus=1,addr=0x41)
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
    def get_brightness(self) -> int:
        payload = self.pi2pi.get_payload('g',[])
        return payload[0]
    def set_brightness(self,start,end,direction,increment):
        payload = self.pi2pi.get_payload('s',[start,end,direction,increment])
        return payload[0]
