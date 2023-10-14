
import datetime
import traceback
import sys

config = {

    "LOG_DATA":{
        "LOG_STATUS":True,
        "LOG_LEVEL":"DEBUG",
    },
}

modes = {
    "DEBUG":0, #all is less
    "INFO":1,
    "WARNING":2, #some
    "ERROR":3,
    "CRITICAL":4 #few is more
}

def _create_entry(code,short_error,level,data):
    log_entry = f"{datetime.datetime.now()} | {config['LOG_DATA']['LOG_LEVEL']} | {level} | {modes[level]} | {code} | {short_error} | \n {data} \n"
    return log_entry

def log(log_level:int,code,message,data):
    current_level = config["LOG_DATA"]["LOG_LEVEL"]
    if current_level <= log_level:
        entry = _create_entry(code,message,current_level,data)


date = datetime.datetime.now()
def format_error(e):
    formated = traceback.format_exc()
    print(f"FUNCTION STARTS HERE: {formated}")

try:
    print(date[100])
except Exception as e:
    format_error(e)
    formated = traceback.format_exc()
    print(15,formated)

import glob
from dominate import document
from dominate.tags import *

class Document:

    photos = glob.glob('photos/*.jpg')

    with document(title='Photos') as doc:
        h1('Photos')
        for path in photos:
            div(img(src=path), _class='photo')


    with open('gallery.html', 'w') as f:
        f.write(doc.render())


