#import all packages in PiZero/dyson_lib
from DIYson_lib.Serialization import serialize, deserialize
from DIYson_lib.Hardware import Sensor,HW
from DIYson_lib.i2c import PI2PI_I2C
#initialize the i2c class
pi2pi = PI2PI_I2C()
#initialize the hardware class
hw = HW()
#initialize the sensor class
#sensor = Sensor()

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from API.routes.api import router as api_router
import json
import os


with open(os.path.dirname(__file__) + '/DIYson_lib/config.json') as json_file: #load config.json
            config = json.load(json_file)
if config["LAMP_DATA"]["WIFI"]:
    app = FastAPI()

    origins = ["http://localhost:8005"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    if __name__ == '__main__':
        uvicorn.run("main:app", host=str(config["SERVER_DATA"]["IP"]), port=int(config["SERVER_DATA"]["PORT"]), log_level="info", reload=True)
        print("running")