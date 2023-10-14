
import qrcode
import cv2
import os
import json

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
    return img

