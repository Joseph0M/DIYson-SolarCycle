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
#i2cdetect -y 1
import sys
import smbus2 as smbus#,smbus2
import time
from DIYson_lib.Serialization import serialize,deserialize
class PI2PI_I2C:
    def __init__(self,bus:int = 1,addr:int = 0x41) -> None:
        self.bus = smbus.SMBus(bus)
        self.addr = int(addr)

    def deinit(self):
        self.bus.close()
        del self.bus
        del self.addr
    def write(self,data:list):
        for i in data:
            self.bus.write_byte(self.addr, i)
            time.sleep(0.075)
    def read(self):
        data = []
        bit = 0
        while bit != 4:
            bit=self.bus.read_byte(self.addr)
            data.append(bit)
            time.sleep(0.01)
        return data
    def get_payload(self,name:str,args:list) -> list:
        data = serialize(False,name,*args)
        self.write(data)
        print(name)
        read = self.read()
        print(read)
        response = deserialize(read)
        for i in response:
            if i[0] == name:
                return i[1]
        return [0]
    def get_generic_payload(self):
        data = serialize(False,'generic',*[])
        self.write(data)
        response = deserialize(self.read())
        return response
    def send_payload(self,name:str,args:list) -> None:
        data = serialize(False,name,*args)
        self.write(data) 