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
        self.pi2pi = PI2PI_I2C(bus=1,addr=0x41)
    def get_distance_from_object(self,range:int = 1,timing:int = 0) -> int:
        payload = self.pi2pi.get_payload('get_distance_from_object',[range,timing])
        return payload[0]

    def focus_roi(self,range:int = 1,type:str = "w"):
        #NOT AVALIBLE ON SLAVE
        return NotImplementedError

    def get_ambient_light(self) -> int:
        payload = self.pi2pi.get_payload('get_ambient_light',[])
        return payload[0]

    def get_proximity(self):
        payload = self.pi2pi.get_payload('get_proximity',[])
        return payload[0]

class HW():
    def __init__(self) -> None:
        self.pi2pi = PI2PI_I2C(bus=1,addr=0x41)
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
    def get_brightness(self) -> int:
        payload = self.pi2pi.get_payload('get_brightness',[])
        return payload[0]
    def set_brightness(self,start,end,direction,increment):
        payload = self.pi2pi.get_payload('set_brightness',[start,end,direction,increment])
        return payload[0]
