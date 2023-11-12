"""Implimnetation of AutoMode using threading. CPU with more than one core is required to run this."""
import time
import os
import json
import logging
import threading
from .Hardware import hw,als,tof,ps
#from scipy.signal import find_peaks

class Graphing:
    """ Graphing Class
    Used to extrapolate data from sensors to LED brightness"""
    def __init__(self):
        self.start = False
        with open(os.path.dirname(__file__) + '/config.json',"rt",encoding='utf-8') as json_file:
            self.config = json.load(json_file)

    def ease(self,x,start,end,period):
        """Ease in-out function"""
        value_range = end-start
        y = x * x * (3.0 - 2.0 * x)*value_range
        return(x*period,y)

    def distance(self,distance:float):
        """Extrapolates distance data to LED brightness.
        uses y=mx+c where graph is negative to extrapolate data"""
        max_d = self.config["CONFIG_DATA"]["MAX_DIST"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]
        y=((min_b - max_b)/(max_d-min_b)*distance)+max_b
        return max(min(y, max_b), min_b)

    def proximity(self,proximity:float):
        """Extrapolates proximity data to LED brightness.
        uses y=mx+c where graph is  positive to extrapolate data"""
        max_p = self.config["CONFIG_DATA"]["MAX_PROX"]
        min_p = self.config["CONFIG_DATA"]["MIN_PROX"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]+min_b
        y=((min_b - max_b)/(min_p-max_p)*proximity)+max_b
        return max(min(y, max_b), min_b)

    def lux(self,lux:float):
        """Extrapolates lux data to LED brightness.
        uses y=mx+c where graph is positive to extrapolate data"""
        max_l = self.config["CONFIG_DATA"]["MAX_LUX"]
        min_l = self.config["CONFIG_DATA"]["MIN_LUX"]
        min_b = self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"]
        max_b = self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"]
        y=(min_b - max_b)/(min_l-max_l)*lux
        return max(min(y, max_b), min_b)
class Ajustment:
    """Ajusts LED Brightness and CCT based on sensor data."""
    def __init__(self):
        self._cct = 0
        self._intensity = 0

        self._ambientLight = 0
        self._proximity = 0
        self._distance = 0
        with open(os.path.dirname(__file__) + '/config.json',"rt",encoding='utf-8') as json_file:
            self.config = json.load(json_file)

    def verify(self,value:float,maxVal:float,minVal:float):
        """Verifies that value is between maximum and minimum allowed values."""
        return max(min(value, maxVal), minVal)
    def ambientLightCorrection(self,light:float) -> float:
        """Corrects the LED Intensity based on the chage of ambient light in a given room."""
        changeOfAL = light-self._ambientLight
        intensity += changeOfAL
        intensity = self.verify(intensity,self.config["LED_DATA"]["BRIGHTNESS"]["MAX_BRI"],self.config["LED_DATA"]["BRIGHTNESS"]["MIN_BRI"])
        self._intensity = intensity
        self._ambientLight = light
        return intensity
    def distanceCorrection(self,distance:float) -> float:
        intensity = 1/(distance**2)
        changeOfIntensity = intensity-self._intensity
        self._intensity =+ changeOfIntensity
        return self._intensity

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s (T:%(thread)d):- %(message)s")
MODE = "ALS"
AUTO = Graphing()
HW = hw()
class Auto(threading.Thread):
    """AutoMode Thread.
    Used to run the sensors in the background and update the LED brightness accordingly."""
    def __init__(self, mode, freq):
        self._running = True
        self.cycle = 0
        self.mode = mode
        self.freq = freq
        threading.Thread.__init__(self)

    def terminate(self) -> None:
        """Terminates the current thread"""
        self._running = False
        logging.info("Terminating AutoMode Thread")

    def run(self) -> None:
        """Runs the current thread with desired mode and frequency."""

        logging.info(
            "Starting AutoMode Thread | Sensor Type: %s | Frequency: %s", 
            self.mode,
            self.freq
            )

        self.cycle = 0
        if self.mode == "ALS":
            sensor = als()
            graph = AUTO.lux
            logging.info("Bound Mode Data to Sensor | %s",self.mode)

        elif self.mode == "TOF":
            sensor = tof()
            graph = AUTO.distance

        elif self.mode == "PS":
            sensor = ps()
            graph = AUTO.proximity

        else:
            logging.error("Invalid Mode")
            self.terminate()

        logging.info("Bound Mode Data to Sensor | Sensor: %s | Graph: %s",self.mode,graph.__name__)

        while self._running:
            time.sleep(int(self.freq)) #Five second delay
            logging.info(
                "AutoMode Iteration %s | %s | %s | %s",
                self.cycle,
                self.mode,
                self.freq,
                graph.__name__
                )

            self.cycle += 1.0
            data = sensor.get()
            value = graph(data)
            HW.set_brightness(value)
            logging.info(
                "AutoMode Iteration %s | %s | %s | %s | Data; Sensor: %s | Value: %s",
                self.cycle, self.mode, self.freq, graph.__name__, data, value
                )

t1 = Auto("ALS", 5)
t1.start()
