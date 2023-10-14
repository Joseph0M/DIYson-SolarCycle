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
import os
import json
import smbus2 as smbus#,smbus2
import time
#from DIYson_lib.Serialization import serialize,_deserialize


def _serialize(multi: bool, function_name, *args):
    serialized_data = []
    if not multi:
        serialized_data.append(1)
    serialized_data.extend(ord(char) for char in function_name)
    serialized_data.append(0)  # Data break
    for arg in args:
        if isinstance(arg, str):
            serialized_data.extend(ord(char) for char in arg)
        elif isinstance(arg, float):
            serialized_data.extend(ord(char) for char in str(arg))
        elif isinstance(arg, int):
            serialized_data.extend(ord(char) for char in str(arg))
        elif isinstance(arg, bool):
            serialized_data.extend([ord('T' if arg else 'F')])
        serialized_data.append(0)  # Data break
    if not multi:
        serialized_data.append(4)
    return serialized_data
def _deserialize(serialized_data):
    if serialized_data[0] == 1:
        serialized_data = serialized_data[1:]
    if serialized_data[-1] == 4:
        serialized_data = serialized_data[:-1]
    function_name = ''
    args = []
    current_arg = ''
    array = []
    multi_func = False
    for ascii_int in serialized_data:
        if ascii_int == 0:
            if not function_name:
                function_name = current_arg
            else:
                args.append(current_arg)
            current_arg = ''
        elif ascii_int == 23:
            multi_func = True
            array.append([function_name, args])
            function_name = ''
            args = []
            current_arg = ''
        else:
            current_arg += chr(ascii_int)
    array.append([function_name, args])
    _deserialized_array = []
    for function in array:
        deserialized_args = []
        for arg in function[1]:
            if arg.isdigit():
                deserialized_args.append(int(arg))
            elif arg.replace('.', '', 1).isdigit():
                deserialized_args.append(float(arg))
            elif arg == 'True':
                deserialized_args.append(True)
            elif arg == 'False':
                deserialized_args.append(False)
            else:
                deserialized_args.append(arg)
        _deserialized_array.append([function[0], deserialized_args])
    return _deserialized_array

class I2C:
    def __init__(self,bus:int = 11,addr:int = 0x41) -> None:
        self.bus = smbus.SMBus(bus)
        self.addr = int(addr)
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)

    def deinit(self):
        self.bus.close()
        del self.bus
        del self.addr
    def write(self,data:list):
        for i in data:
            self.bus.write_byte(self.addr, i)
            time.sleep(0.075)
    def read(self,addr):
        data = []
        bit = 0
        while bit != 4:
            bit=self.bus.read_byte(self.addr)
            data.append(bit)
            time.sleep(0.01)
        return data
    def validate(self):
        addresses = [int(self.config["LAMP_DATA"]["ADDR"],16),int(self.config["SENSOR_DATA"]["PS"]["ADDR"],16),int(self.config["SENSOR_DATA"]["ALS"]["ADDR"],16)]
        try:
            for addr in addresses:
                self.read(addr)
            return True
        except Exception as error:
            if self.config["LOG_DATA"]["LOG_STATUS"] and self.config["LOG_DATA"]["LOG_LEVEL"] == "DEBUG":
                with open(os.path.dirname(__file__) + '/'+self.config["LOG_DATA"]["LOG_FILE"],'a') as log:
                    log.write(f'{error}')
            return False
            
    def get_payload(self,name:str,args:list) -> list:
        data = _serialize(False,name,*args)
        self.write(data)
        print(name)
        read = self.read(self.addr)
        print(read)
        response = _deserialize(read)
        for i in response:
            if i[0] == name:
                return i[1]
        return [0]
    def get_generic_payload(self):
        data = _serialize(False,'generic',*[])
        self.write(data)
        response = _deserialize(self.read(self.addr))
        return response
    def send_payload(self,name:str,args:list) -> None:
        data = _serialize(False,name,*args)
        self.write(data) 

class OneWire:
    def __init__(self) -> None:
        self.owfile = '/sys/bus/w1/devices/'
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
    def save_data(self,index:list,data):
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            config = json.load(json_file)
            config[index[0]][index[1]] = data
            json_file.seek(0)
            json.dump(config, json_file, indent=4)
            json_file.truncate()
    def get_i2cbus(self):
        i2c_dir = '/dev'
        i2c_buses = []
        for filename in os.listdir(i2c_dir):
            if filename.startswith('i2c-'):
                try:
                    bus_num = int(filename.split('-')[1])
                    i2c_buses.append(bus_num)
                except ValueError:
                    pass
        i2c_buses.remove(1)
        i2c_buses.remove(2)
        return i2c_buses[0]
    def get_serial(self):
        device_dir = '/sys/bus/w1/devices' 
        devices = [f.path for f in os.scandir(device_dir) if f.is_dir()]
        serials = [os.path.basename(d) for d in devices if d.startswith(os.path.join(device_dir, '19-'))]
        valid = self.validate_serial(serials[0])
        if valid:
            return serials[0]
        else:
            return False
    def validate_serial(self,serial):
        if serial.startswith('19-') and serial == self.config["LAMP_DATA"]["SERIAL"]:
            return True
        else:
            return False