import json
import os.path
import importlib
from typing import Optional, Literal

import smbus
import deprecation
from .protocol import I2C

with open(os.path.dirname(__file__) + '/config.json',"rt",encoding="utf-8") as json_file: #load config.json
    config = json.load(json_file)

MODULE_MAP = {
    "LTR559": "ltr559:LTR559",
    "APDS9960": ["apds9960.const", "apds9960:APDS9960"],
    "VL53L1X": "VL53L1X:VL53L1X",
    "VL53L1X_RoI": "VL53L1X",
}
# syntax:
# module_name:class_name
# package_name.module_name
# package_name.module_name:class_name

IMPORTED_MODULES = {}
def _get_module(sensor_type,return_index:Optional[int] = -1):
    """ dynamically imports a module based on the sensor type. returns the module class.
    Args:
        sensor_type (str): The sensor type to import.
        return_index (int, optional): The index of the module to return. Defaults to -1.
            -1 = last module referenced in MODULE_MAP
            -2 = return all modules referenced in MODULE_MAP
    Raises:
        ValueError: Invalid sensor type"""
    __version__ = "1.0.0-beta1"
    attr = None
    if sensor_type not in MODULE_MAP:
        raise ValueError("Invalid sensor type")
    module_name = MODULE_MAP[sensor_type]
    if isinstance(module_name, list):
        module_list = module_name
        return_modules = []
        for module_name in module_list:
            if module_name not in IMPORTED_MODULES:
                if ":" in module_name:
                    module,attr = module_name.split(":")
                    imported_module = importlib.import_module(module)
                else:
                    imported_module = importlib.import_module(module_name)
                IMPORTED_MODULES[module_name] = imported_module
                if attr is not None:
                    sensor_class = getattr(IMPORTED_MODULES[module_name], attr)
                    return_modules.append(sensor_class)
                else:
                    sensor_class = IMPORTED_MODULES[module_name]
                    return_modules.append(sensor_class)
            else:
                if attr is not None:
                    sensor_class = getattr(IMPORTED_MODULES[module_name], attr)
                    return_modules.append(sensor_class)
                else:
                    sensor_class = IMPORTED_MODULES[module_name]
                    return_modules.append(sensor_class)
        if return_index == -2:
            return return_modules
        elif return_index > -1:
            return return_modules[return_index]
        else:
            return return_modules[return_index]
    if module_name not in IMPORTED_MODULES:
        if ":" in module_name:
            module,attr = module_name.split(":")
            imported_module = importlib.import_module(module)
        else:
            imported_module = importlib.import_module(module_name)
        IMPORTED_MODULES[module_name] = imported_module
        if attr is not None:
            sensor_class = getattr(IMPORTED_MODULES[module_name], attr)
        else:
            sensor_class = IMPORTED_MODULES[module_name]
    else:
        if attr is not None:
            sensor_class = getattr(IMPORTED_MODULES[module_name], attr)
        else:
            sensor_class = IMPORTED_MODULES[module_name]
    return sensor_class

class ToF(_get_module("VL53L1X",return_index=-1)):
    """Python support for VL53L1X Time of Flight Sensor. 
        See Module and documentation here: https://github.com/pimoroni/vl53l1x-python"""
    __version__ = "1.0.0-beta1"
    def __init__(self) -> None:
        self.roiModule = _get_module("VL53L1X_RoI",return_index=-1)
        self.focus = self.focus_roi("w")
        self.timing = 33
        self.range = 1

    def get(self) -> float:
        """Get the distance from the sensor in mm. returns raw distance as float."""
        with self.open():
            self.set_user_roi(self.focus)
            self.start_ranging(self.range)
            distance = self.get_distance()
            self.stop_ranging()
            return distance

    def focus_roi(self,region:Optional[Literal["w","c","t","b","l","r"]] ="w") -> None:
        """Set the focus of the sensor using region."""
        roi = {
            "w":self.roiModule.VL53L1xUserRoi(0, 15, 15, 0),
            "c":self.roiModule.VL53L1xUserRoi(6, 9, 9, 6),
            "t":self.roiModule.VL53L1xUserRoi(6, 15, 9, 12),
            "b":self.roiModule.VL53L1xUserRoi(6, 3, 9, 0),
            "l":self.roiModule.VL53L1xUserRoi(0, 9, 3, 6),
            "r":self.roiModule.VL53L1xUserRoi(12, 9, 15, 6),
        }
        try:
            return roi[region]
        except KeyError:
            return roi["w"]

class ALS(_get_module("LTR559",return_index=-1)):
    """Python support for LTR-559 Abient Light and Proximity Sensor.
        See Module and documentation here: https://github.com/pimoroni/ltr559-python
        Functions is depreciated."""
    __version__ = "1.0.0-beta1"
    def __init__(self) -> None:
        super().__init__()

    @deprecation.deprecated(deprecated_in="1.0.0-alpha3", removed_in="1.0.0-beta2",
                        current_version=__version__,
                        details="Use APDS9960 Sensor instead.")    
    def get(self) -> float:
        """Get the ambient light level from the sensor in lux."""
        self.update_sensor()
        lux = self.get_lux()
        return lux

class PS_LTR559(_get_module("LTR559",return_index=-1)):
    """Python support for LTR-559 Abient Light and Proximity Sensor.
        See Module and documentation here: https://github.com/pimoroni/ltr559-python
        Functions is depreciated."""
    __version__ = "1.0.0-beta1"
    def __init__(self) -> None:
        super().__init__()

    @deprecation.deprecated(deprecated_in="1.0.0-alpha3", removed_in="1.0.0-beta2",
                        current_version=__version__,
                        details="Use APDS9960 Sensor instead.")
    def get(self) -> float:
        """Get the proximity level from the sensor."""
        self.update_sensor()
        prox = self.get_proximity()
        return prox
    
class PS(_get_module("APDS9960",return_index=-1)):
    """Python support for APDS9960 Abient Light, Proximity, RGB Colour and Gesture Sensor. 
        See Module and documentation here: https://github.com/liske/python-apds9960"""
    __version__ = "1.0.0-beta1"
    def __init__(self) -> None:
        self.bus = smbus.SMBus(config["SENSOR_DATA"]["BUS"])
        self.addr = int(config["SENSOR_DATA"]["PS"]["ADDR"],16)   
        self.enableProximitySensor()
        super().__init__()
    def get(self) -> float:
        """Get the proximity level from the sensor."""
        self.setProximityIntLowThreshold(50)
        self.enableProximitySensor()
        prox = self.readProximity()
        return prox


class hw():
    """Maniplate perameters of the hardware connected via the data bus."""
    __version__ = "1.0.0-beta1"
    def __init__(self) -> None:
        with open(os.path.dirname(__file__) + '/config.json',encoding="utf-8") as json_file: #load config.json
            self.config = json.load(json_file)
        self.pi2pi = I2C(bus=self.config["SENSOR_DATA"]["BUS"],addr=int(self.config["LAMP_DATA"]["ADDR"],16))
    def getBrightness(self) -> int:
        """Set Brightness of the LED Module using the data bus."""
        payload = self.pi2pi.get_payload('g',[])
        return payload[0]
    def setBrightness(self,start,end,direction,increment) -> int:
        """Set Brightness of the LED Module using the data bus."""
        payload = self.pi2pi.get_payload('s',[start,end,direction,increment])
        return payload[0]