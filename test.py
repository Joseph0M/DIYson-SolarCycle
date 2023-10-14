from scipy.signal import find_peaks
import time
import os
import json

class Graphing:
    def __init__(self):
        self.start = False
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
    def ease(self,x,start,end,period):
        range = end-start
        y = x * x * (3.0 - 2.0 * x)*range
        return(x*period,y)

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

import logging
import threading
import time
from .Hardware import hw,als,tof,ps
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s (T:%(thread)d):- %(message)s")
mode = "ALS"

global cycle
cycle = 0.0
AUTO = Graphing()
HW = hw()
class Auto(threading.Thread):  
    def __init__(self,mode):
        self._running = True
        self.cycle = 0
        threading.Thread.__init__(self)

    def terminate(self):  
        self._running = False  
        logging.info("Terminating AutoMode Thread")

    def run(self,mode,freq):
        logging.info(f"Starting AutoMode Thread | Sensor Type: {mode} | Frequency: {freq}")
        self.cycle = 0
        if mode == "ALS":
            sensor = als()
            graph = AUTO.lux_auto
            logging.info(f"Bound Mode Data to Sensor | {mode}")
        elif mode == "TOF":
            sensor = tof()
            graph = AUTO.distance_auto
        elif mode == "PS":
            sensor = ps()
            graph = AUTO.proximity_auto
        else:
            logging.error("Invalid Mode")
            self.terminate()
        logging.info(f"Bound Mode Data to Sensor | Sensor: {mode} | Graph: {graph.__name__}")
        while self._running:
            time.sleep(int(freq)) #Five second delay
            logging.info(f"AutoMode Iteration {self.cycle} | {mode} | {freq} | {graph.__name__}")
            self.cycle += 1.0
            data = sensor.get()
            value = graph(data)
            HW.set_brightness(value)
            logging.info(f"AutoMode Iteration {self.cycle} | {mode} | {freq} | {graph.__name__} | Data; Sensor: {data} | Value: {value}")

t1 = Auto()
t1.start()
