
import os
import json
import pickle
import base64
import datetime
import qrcode

with open(os.path.dirname(__file__) + '/config.json') as json_file: #load config.json
            config = json.load(json_file)

def encodeQR(code):
    server = config['SERVER_DATA']
    link  = f"https://{server['IP']}:{server['PORT']}/log/{code}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
        )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
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
def _create_error(code,short_error,data):
    date = datetime.datetime.now()
    error = _encode_log(f"CRITICAL ERROR ENCOUNTERED: {short_error}; CANNOT PROCEED: CODE:{str(code)};DTSTART/{date}/DTEND; DATA:{data}")
    return error

modes = {
    "DEBUG":0,
    "INFO":1,
    "WARNING":2,
    "ERROR":3,
    "CRITICAL":4
}
def log(code, error,data):
    if config["LOG_DATA"]["LOG_LEVEL"] == "DEBUG" and config["LOG_DATA"]["LOG_STATUS"] == True:
        if isinstance(data,list):
            encoded_data = ""
            for i in data:
                encoded_data += _encode_log(i)
        else:
            encoded_data = _encode_log(data)
        complete_error = _create_error(f"{code}",repr(error),encoded_data)
        log = _read_log()
        log.append(complete_error)
        if _write_log(log):
            return True
        else:
            return False


try:
      a = 1+"s"
except Exception as e:
    log(0x12,e,"test")

print(_read_log())