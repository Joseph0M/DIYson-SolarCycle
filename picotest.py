import board
import touchio
from i2ctarget import I2CTarget
from lib.DIYson import HW
import asyncio
#sensor = Sensor()
hw = HW()

current_read = False
current_write = False
read_buffer = []
write_buffer = []
bit_acknolagment = False
##############################################################################################################

def serialize(multi: bool, function_name, *args):
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
def deserialize(serialized_data):
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
            if function_name:
                args.append(current_arg)
                current_arg = ''
                array.append([function_name, args])
                function_name = ''
                args = []
            else:
                multi_func = True
        else:
            current_arg += chr(ascii_int)
    if function_name:
        args.append(current_arg)
        array.append([function_name, args])
    elif multi_func:
        array.append(['', []])
    deserialized_array = []
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
        deserialized_array.append([function[0], deserialized_args])
    return deserialized_array

def multi_function_serial(serialized_data):
    buffer = [1]
    for i, individual_func in enumerate(serialized_data):
        if individual_func[0] == '' and individual_func[1] == []:
            continue
        buffer += individual_func
        if i < len(serialized_data) - 1:
            buffer.append(23)
    buffer.append(4)
    return buffer
##############################################################################################################
def get_func_name(buffer):
    names = []
    if len(buffer)>1:
        for function in buffer:
            names.append(function[0])
        return names
    else:
        return buffer[0][0]
def get_args(buffer,index):
    return buffer[index][1]


class readwrite:
    def __init__(self) -> None:
        self.current_read = False
        self.current_write = False
        self.read_buffer = []
        self.write_buffer = []
        self.write_index = 0
        self.bit_acknolagment = False

    def read(self,request):
        bit = request.read(ack=False)
        if bit == '\x00' and not self.current_read: #ack bit is 0 if not current read
            self.bit_acknolagment = True
        elif bit == '\xff': #ack bit is always ff
            self.bit_acknolagment = True
            return None
        elif bit == '\x01':
            self.current_read = True
            self.read_buffer.append(1)
        elif bit == '\x04':
            self.current_read = False
            self.read_buffer.append(4)
            buffer = self.read_buffer
            self.read_buffer = []
            return buffer
        elif self.current_read:
            self.read_buffer.append(ord(bit.decode()))
        
    def write(self, request):
        write = False
        if self.current_write:
            write = True
        elif self.write_index < len(self.write_buffer) and self.write_buffer[self.write_index] == 1:
            self.current_write = True
            write = True
        if write:
            if self.write_index < len(self.write_buffer):
                request.write(chr(self.write_buffer[self.write_index]))
                self.write_index += 1
                self.bit_acknolagment = False
                if self.write_index == len(self.write_buffer) and self.write_buffer[self.write_index-1] == 4:
                    self.current_write = False
                    self.write_index = 0
                    print(self.write_buffer)
                    if payloadmode == 'sT':
                        try:
                            hw.set_brightness(array[0][1][0],array[0][1][1],array[0][1][2],array[0][1][3])
                        except TypeError or IndexError:
                            pass
            else:
                print("Error: Index out of range")
def update_data(rw,mode='generic'):
    write_buffer = []
    if not rw.current_write:
        if mode == 'bri':
            write_buffer = serialize(False, "g", *[hw.get_brightness()])
        elif mode == 'sT':
            write_buffer = serialize(False, "s", *[True])
        elif mode == 'sF':
            write_buffer = serialize(False, "s", *[False])
        if write_buffer != []:
            rw.write_buffer = write_buffer


payloadmode = 'g'
rw = readwrite()
target = I2CTarget(board.GP3, board.GP2, [0x41]) #data register: 0x11

onoff = touch = touchio.TouchIn(board.GP26)
plus = touchio.TouchIn(board.GP27)
minus = touchio.TouchIn(board.GP28)

increment,change = 1,5 #increment: how much it changes by every loop, change: how much it changes by when pressing plus or minus

while True:
    update_data(rw,payloadmode)
    request = target.request()
    if onoff.value:
        hw.set_brightness(None,0,1,increment,["sgf"])
    elif plus.value:
        hw.set_brightness(None,None,1,increment,["i",change])
    elif minus.value:
        hw.set_brightness(None,None,-1,increment,["i",-change])
    if request is not None:
        if request.is_read:
            rw.write(request)
            print("write",payloadmode)
        else:
            print("read")
            array = rw.read(request)
            print(array)
            if array:
                try:
                    array = deserialize(array)
                    if get_func_name(array) == 'g':
                        payloadmode = 'bri'
                        update_data(rw,payloadmode)
                    elif get_func_name(array) == 's':
                        payloadmode = 'sT'
                        update_data(rw,payloadmode)
                except IndexError:
                    print(array)