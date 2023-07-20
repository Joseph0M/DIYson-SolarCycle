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
import math
import board

class HW():
    def __init__(self,pin=board.GP15) -> None:
        import pwmio
        self.pwm_freq = 1000
        self.pwm = pwmio.PWMOut(pin, frequency=self.pwm_freq, duty_cycle=0)
        
    def set_brightness(self,start,end,direction,increment,mode:list=['f']):
        if mode[0] == 'f':
            for cycle in range(int(start), int(end), int(direction)):
                self.pwm.duty_cycle = int(cycle / 100 * 65535)
                time.sleep(0.25 / increment)
        elif mode[0] == 's':
            self.pwm.duty_cycle = int(end / 100 * 65535)
        elif mode[0] == 'sgf':
            start = self.get_brightness()
            for cycle in range(int(start), int(end), int(direction)):
                self.pwm.duty_cycle = int(cycle / 100 * 65535)
                time.sleep(0.25 / increment)
        elif mode[0] == 'i':
            start = self.get_brightness()
            end = start+mode[1]
            for cycle in range(int(start), int(end), int(direction)):
                self.pwm.duty_cycle = int(cycle / 100 * 65535)
                time.sleep(0.25 / increment)
    def get_brightness(self):
        return (int(self.pwm.duty_cycle)/65535)*100