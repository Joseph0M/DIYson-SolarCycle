import os
import json
import pickle
import base64
import datetime
import traceback

modes = {
    "DEBUG":0,
    "INFO":1,
    "WARNING":2,
    "ERROR":3,
    "CRITICAL":4
}

with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            config = json.load(json_file)

def _read_log() -> list:
    with open(os.path.dirname(__file__) + '/log.diyson',"rb") as log_file: #load log.diyson
                log = pickle.load(log_file)
    return log

def _write_log(data):
    try:
        with open(os.path.dirname(__file__) + '/log.diyson','wb') as log_file: #load config.json
                    pickle.dump(data,log_file)
        return True
    except:
        return False
def _clear_log():
    data = []
    return _write_log(data)

def _encode_log(data):
    serialised_data = base64.b64encode(bytes(data, 'utf-8')).decode("utf-8")
    return serialised_data
def _decode_log(data):
    serialised_data = base64.b64decode(data).decode("utf-8")
    return serialised_data

def _create_entry(code,short_error,level,data):
    error = f"{datetime.datetime.now()} | {config['LOG_DATA']['LOG_LEVEL']} | {level} | {modes[level]} | {code} | {short_error} | \n {data} \n"
    return error
    tb = formated = traceback.format_exc()

def log(code, message,data,level = 4):
    level = modes[config["LOG_DATA"]["LOG_LEVEL"]]
    if level >= 4 and config["LOG_DATA"]["LOG_STATUS"] == True:
        if isinstance(data,list):
            encoded_data = ""
            for i in data:
                encoded_data += _encode_log(i)
        else:
            encoded_data = _encode_log(data)
        complete_error = _create_error(f"{code}",repr(message),encoded_data)
        log = _read_log()
        log.append(complete_error)
        if _write_log(log):
            return True
        else:
            return False
        
def log(code, message,data,level = 4):
    level = modes[config["LOG_DATA"]["LOG_LEVEL"]]
    if level >= 4 and config["LOG_DATA"]["LOG_STATUS"] == True:

        if isinstance(data,list):
            encoded_data = ""
            for i in data:
                encoded_data += _encode_log(i)
        else:
            encoded_data = _encode_log(data)
        complete_error = _create_error(f"{code}",repr(message),encoded_data)
        log = _read_log()
        log.append(complete_error)
        if _write_log(log):
            return True
        else:
            return False
        
        