import importlib

MODULE_MAP = {
    "LTR559": "ltr559:LTR559",
    "APDS9960": ["apds9960.const", "apds9960:APDS9960"],
    "VL53L1X": "VL53L1X:VL53L1X",
    "VL53L1X1": "VL53L1X",
}
# syntax:
# module_name:class_name
# package_name.module_name
# package_name.module_name:class_name
# Does not support fucntion calls

IMPORTED_MODULES = {}
def _get_module(sensor_type,return_index:int = -1):
    """ dynamically imports a module based on the sensor type. returns the module class.
    Args:
        sensor_type (str): The sensor type to import.
        return_index (int, optional): The index of the module to return. Defaults to -1.
            -1 = last module referenced in MODULE_MAP
            -2 = return all modules referenced in MODULE_MAP
    Raises:
        ValueError: Invalid sensor type"""
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
a = _get_module("VL53L1X1",return_index=-1)
a.VL53L1xUserRoi(0, 15, 15, 0)
print(a)
