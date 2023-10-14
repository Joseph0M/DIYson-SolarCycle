import json
import os.path
import smbus
from .protocol import I2C
import VL53L1X
from ltr559 import LTR559
from warnings import warn as Warn

with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
    config = json.load(json_file)
def hardware_connection_error(*args):
    raise ConnectionError("Hardware Connection Error 0x, check config.json and hardware connections")

if config["SENSOR_DATA"]["ALS"]["MODEL"] == "APDS9960" or config["SENSOR_DATA"]["PS"]["MODEL"] == "APDS9960":
    from apds9960.const import *
    from apds9960 import APDS9960
else:
    APDS9960 = hardware_connection_error

def _get_module(type:str = "ALS") -> None:
    ALS = config["SENSOR_DATA"]["ALS"]["MODEL"]
    PS = config["SENSOR_DATA"]["PS"]["MODEL"]
    TOF = config["SENSOR_DATA"]["TOF"]["MODEL"]
    modules = [ALS,PS,TOF]
    duplicate = ''
    for mod in modules:
        if modules.count(mod) > 1:
            duplicate = mod
    if duplicate == ALS:
        from ltr559 import LTR559
        function =  LTR559()
    elif duplicate == PS:
        from apds9960.const import *
        from apds9960 import APDS996
        function = APDS9960(smbus.SMBus(config["SENSOR_DATA"]["BUS"]))
    elif duplicate == TOF:
        import VL53L1X
        function = VL53L1X.VL53L1X
    
class tof(VL53L1X.VL53L1X):
    def __init__(self) -> None:
        import VL53L1X
        self.focus = self.focus_roi("w")
        self.timing = 33
        self.range = 1
    def get(self) -> float:
        with self.open() as tof_open:
            self.set_user_roi(self.focus)
            self.start_ranging(self.range)
            distance = self.get_distance()
            self.stop_ranging()
            return distance
    def focus_roi(self,type:str = "w"):
        roi = {
            "w":VL53L1X.VL53L1xUserRoi(0, 15, 15, 0),
            "c":VL53L1X.VL53L1xUserRoi(6, 9, 9, 6),
            "t":VL53L1X.VL53L1xUserRoi(6, 15, 9, 12),
            "b":VL53L1X.VL53L1xUserRoi(6, 3, 9, 0),
            "l":VL53L1X.VL53L1xUserRoi(0, 9, 3, 6),
            "r":VL53L1X.VL53L1xUserRoi(12, 9, 15, 6),
        }
        try:
            return roi[type]
        except KeyError:
            return roi["w"]
        
class als(LTR559()):
    def __init__(self) -> None:
        self.__
        self.__doc__ = """Python support for LTR-559 Abient Light and Proximity Sensor. 
        See Module and documentation here: https://github.com/pimoroni/ltr559-python
        Implimentation of the LTR-559 sensor is made by Joseph0M under  The MIT License."""
    def get(self) -> float:
        self.update_sensor()
        lux = self.get_lux()
        Warn("This function is depreciated, switch to APDS9960 Sensor and use als_apds9960().get() instead",DeprecationWarning)
        return lux
        
class ps(LTR559()):
    def __init__(self) -> None:
        self.__doc__ = """Python support for LTR-559 Abient Light and Proximity Sensor. 
        See Module and documentation here: https://github.com/pimoroni/ltr559-python
        Implimentation of the LTR-559 sensor is made by Joseph0M under  The MIT License."""
    def get(self):
        self.update_sensor()
        prox = self.get_proximity()
        Warn("This function is depreciated, switch to APDS9960 Sensor and use ps_apds9960().get() instead",DeprecationWarning)
        return prox
    
class ps_adps9960(APDS9960(smbus.SMBus(config["SENSOR_DATA"]["BUS"]))):
    def __init__(self) -> None:
        self.__doc__ = """Python support for APDS9960 Abient Light, Proximity, RGB Colour and Gesture Sensor. use self.get() to grab proximity data.
        See Module and documentation here: https://github.com/liske/python-apds9960
        Implimentation of the ADPS9960 sensor is made by Joseph0M under The MIT License. 
        Module licenced under the GNU LGPLv3 License."""
        self.bus = smbus.SMBus(config["SENSOR_DATA"]["BUS"])
        self.addr = int(config["SENSOR_DATA"]["PS"]["ADDR"],16)   
        self.enableProximitySensor()
    def get(self):
        self.setProximityIntLowThreshold(50)
        self.enableProximitySensor()
        prox = self.readProximity()
        return prox
    
class Sensor():
    def __init__(self) -> None:
        pass
    def get_distance_from_object(self,*args):
        raise Warning(DeprecationWarning("Use tof().get() instead"))
    def focus_roi(self,*args):
        raise Warning(DeprecationWarning("Use tof().focus_roi() instead"))
    def get_ambient_light(self):
        raise Warning(DeprecationWarning("Use als().get() instead"))
    def get_proximity(self):
        raise Warning(DeprecationWarning("Use ps().get() instead"))

class hw():
    def __init__(self) -> None:
        with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            self.config = json.load(json_file)
        self.pi2pi = I2C(bus=self.config["SENSOR_DATA"]["BUS"],addr=int(self.config["LAMP_DATA"]["ADDR"],16))
    def get_brightness(self) -> int:
        payload = self.pi2pi.get_payload('g',[])
        return payload[0]
    def set_brightness(self,start,end,direction,increment):
        payload = self.pi2pi.get_payload('s',[start,end,direction,increment])
        return payload[0]