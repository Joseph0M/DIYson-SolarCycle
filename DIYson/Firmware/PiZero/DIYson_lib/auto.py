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

from scipy.signal import find_peaks
import time
import os
import json
from .Hardware import Sensor
from .Hardware import HW

hw = HW()
sensor = Sensor()
class Auto:
    def __init__(self):
        self.start = False
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)

    def distance_auto(self,distance:float):
        max_d = self.config["CONFIG_DATA"]["MAX_DIST"]
        min_d = self.config["CONFIG_DATA"]["MIN_DIST"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]
        #y=((max_distance - min_distance)/(min_brightness-max_brightness)*distance)+max_brightness #Linear equation y = mx+c where m= diffy/diffx
        y=((min_b - max_b)/(max_d-min_b)*distance)+max_b
        return max(min(y, max_b), min_b)
    
    def proximity_auto(self,proximity:float):
        max_p = self.config["CONFIG_DATA"]["MAX_PROX"]
        min_p = self.config["CONFIG_DATA"]["MIN_PROX"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]+min_b
        #y=((min_proximity - max_proximity)/(max_brightness-min_brightness)*proximity)+min_proximity #Linear equation y = mx+c where m= diffy/diffx
        y=((min_b - max_b)/(min_p-max_p)*proximity)+max_b
        return max(min(y, max_b), min_b)
    
    def lux_auto(self,lux:float):
        max_l = self.config["CONFIG_DATA"]["MAX_LUX"]
        min_l = self.config["CONFIG_DATA"]["MIN_LUX"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]
        y=((min_b - max_b)/(min_l-max_l)*lux)
        return max(min(y, max_b), min_b)
    
    def detect_peak(self,tolerance:list = [1,1,1],list1:list = [], list2:list = [], list3:list = []) -> tuple:
        # Find the peaks
        peaks1, _ = find_peaks(list1)
        peaks2, _ = find_peaks(list2)
        peaks3, _ = find_peaks(list3)
        # Find the plateaus
        plateaus1 = []
        for i in range(len(list1)):
            if i not in peaks1 and (i == 0 or i == len(list1) - 1 or (list1[i-1] < list1[i] and list1[i+1] < list1[i]) or (list1[i-1] > list1[i] and list1[i+1] > list1[i])):
                plateaus1.append(i)
        plateaus2 = []
        for i in range(len(list2)):
            if i not in peaks2 and (i == 0 or i == len(list2) - 1 or (list2[i-1] < list2[i] and list2[i+1] < list2[i]) or (list2[i-1] > list2[i] and list2[i+1] > list2[i])):
                plateaus2.append(i)
        plateaus3 = []
        for i in range(len(list3)):
            if i not in peaks3 and (i == 0 or i == len(list3) - 1 or (list3[i-1] < list3[i] and list3[i+1] < list3[i]) or (list3[i-1] > list3[i] and list3[i+1] > list3[i])):
                plateaus3.append(i)
        # Find the most consequencial peak
        if plateaus1 and list1[-1]>tolerance[0]:
            plateaus1 = True
        if plateaus3 and list2[-1]>tolerance[1]:
            plateaus3 = True
        if plateaus3 and list3[-1]>tolerance[2]:
            plateaus3 = True

        if plateaus1 or plateaus3 or plateaus3:
            if list1[-1]>list2[-1] and list1[-1]>list3[-1]:
                return 1,plateaus1,plateaus2,plateaus3
            elif list2[-1]>list1[-1] and list2[-1]>list3[-1]:
                return 2,plateaus1,plateaus2,plateaus3
            elif list3[-1]>list1[-1] and list3[-1]>list2[-1]:
                return 3,plateaus1,plateaus2,plateaus3
            else:
                return 0,plateaus1,plateaus2,plateaus3
        else: 
            return 0,plateaus1,plateaus2,plateaus3

    def start_auto(self, auto, freq):
        self.start = auto
        list1, list2, list3 = [0], [0], [0]
        count = 0
        prior_bri = hw.get_brightness()
        while self.start == True:
            time.sleep(freq)
            count += 1
            distance = sensor.get_distance_from_object(range = 1,timing = 0)
            proximity = sensor.get_proximity()
            lux = sensor.get_ambient_light()
            list1.append(lux)
            list2.append(proximity)
            list3.append(distance)
            if count > 20:
                list1.remove(list1[0])
                list2.remove(list2[0])
                list3.remove(list3[0])
            type, p1, p2, p3 = self.detect_peak([1, 1, 1], list1, list2, list3)
            if type == 1:
               bri = self.distance_auto(proximity)
            elif type == 2:
                bri = self.lux_auto(lux)
            else:
                bri = self.distance_auto(distance)
            if bri>prior_bri:
                direction = 1
            else:
                direction = -1
            bri = hw.set_brightness(prior_bri,bri,direction,5)
            print(bri)