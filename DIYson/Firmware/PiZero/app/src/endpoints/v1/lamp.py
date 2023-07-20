"""
MIT License
Copyright (c) 2023 Joseph0M
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from fastapi import Depends, FastAPI, APIRouter, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import uvicorn
import socket
import threading
import time

from datetime import datetime, timedelta
from ...models.v1.security import Token, TokenData, User, UserInDB
from DIYson_lib.solarcycle import Solar
from DIYson_lib.Hardware import HW,Sensor
from DIYson_lib.auto import Auto
from DIYson_lib.protocol import OneWire,I2C
from .security import *
from .lamp import *
router = APIRouter(
    prefix="/v1/lamp",
    tags=["v1-Lamp"],
    responses={404: {"description": "Not found"}},
)
hw = HW()
sensor = Sensor()
i2c = I2C()
OW = OneWire()

class Error_Message(BaseModel):
    message: str = "Error Message"
class Error_Detail(BaseModel):
    detail: str = "Error Detail"
class Success(BaseModel):
    value: float
    user: str

@router.post("/auto/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        403: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Activate Auto mode. Curently unstable over i2c.",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)
async def set_auto_mode(current_user: User = Depends(get_current_active_user), auto: bool = True, frequency: int = 5):
    experimental_mode = hw.config["LAMP_DATA"]["EXPERIMENTAL"]
    if experimental_mode:
        if auto == True:
            thread = threading.Thread(target=Auto().start_auto, args=(auto,frequency))
            thread.start()
            return [{"Auto mode started": frequency, "user": current_user.username}]
    else:
        raise HTTPException(status_code=403, detail="Experimental mode is disabled.")
    
@router.post("/set_bri/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        500: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Set the Brightness of the lamp over the 1-Wire or I2C bus.",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)
async def set_lamp_brightness(current_user: User = Depends(get_current_active_user),bri: int = 0,increment: int = 5,yeild: bool = True):
    try:
        current_bri = hw.get_brightness()
        wait_time = abs(int(bri) - int(current_bri)) / abs(int(increment)) * 0.25 / int(increment)
        if bri > int(current_bri):
            direction = 1
        else:
            direction = -1
        print(direction,bri,current_bri)
        try:
            hw.set_brightness(start=current_bri, end=bri,direction=direction,increment=increment)
        except Exception as e:
            return [{"error-04:": e, "user": current_user.username}]
        if yeild:
            time.sleep(wait_time*1.25)
            bri = hw.get_brightness()
            return [{"bri": bri, "user": current_user.username}]
        else:
            return [{"bri": None,"wait":wait_time, "user": current_user.username}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=repr(e))
@router.post("/set_cct/")
async def set_lamp_CCT(current_user: User = Depends(get_current_active_user),cct: int = 5000):
        return [{"cct:": 'NotImplemented', "user": current_user.username}]

@router.get("/get_brightness/")
async def get_brightness(current_user: User = Depends(get_current_active_user)):
    experimental_mode = hw.config["LAMP_DATA"]["EXPERIMENTAL"]
    try:
        bri = hw.get_brightness()
    except Exception as e:
        return [{"error-06:": e, "user": current_user.username}]
    return [{"INTENSITY:": bri, "user": current_user.username}]

@router.get("/get_cct/")
async def get_cct(current_user: User = Depends(get_current_active_user)):
    return [{"CCT:": 'NotImplemented', "user": current_user.username}] 

@router.get("/get_distance/")
async def get_distance(current_user: User = Depends(get_current_active_user),range: int = 1):
    try:
        distance = sensor.get_distance_from_object(range = range)
    except Exception as e:
        return [{"error-07:": e, "user": current_user.username}]
    
    return [{"DISTANCE:": distance,"user": current_user.username}]

@router.get("/get_ambient_light/")
async def get_ambient_light(current_user: User = Depends(get_current_active_user)):
    try:
        al = sensor.get_ambient_light()
        return [{"AMBIENT_LIGHT:": al, "user": current_user.username}]
    except Exception as e:
        return [{"error-08:": e, "user": current_user.username}]

@router.get("/get_proximity/")
async def get_proximity(current_user: User = Depends(get_current_active_user)):
    try:
        prox = sensor.get_proximity()
    except Exception as e:
        return [{"error-09:": e, "user": current_user.username}]
    return [{"PROXIMITY:": prox, "user": current_user.username}]

@router.get("/get_serial/")
async def get_serial_number(current_user: User = Depends(get_current_active_user)):
    return [{"BUS":OW.get_i2cbus(),"SERIAL:": OW.get_serial(), "user": current_user.username}]
@router.get("/verify/")
async def validate_hardware(current_user: User = Depends(get_current_active_user)):
    if OW.validate_serial(OW.get_serial()) and i2c.validate():
        return [{"HW": True, "user": current_user.username}]