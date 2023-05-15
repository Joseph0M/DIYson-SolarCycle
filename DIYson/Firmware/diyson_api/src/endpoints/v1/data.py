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

from datetime import datetime, timedelta
from ...models.v1.security import Token, TokenData, User, UserInDB
from ...models.v1.data import lampData

from ....lib.SolarCycle.solarcycle import Solar
from ....lib.Lamp.Hardware import HW
from ....lib.Lamp.Hardware import Sensor
from .security import *
from .lamp import *
router = APIRouter(
    prefix="/v1/lamp",
    tags=["v1-Lamp"],
    responses={404: {"description": "Not found"}},
)

@router.post("/set_bri/")
async def set_lamp_brightness(current_user: User = Depends(get_current_active_user),bri: int = 100,incriment: int = 1):
    if lampData.status != "BUSY":
        if bri > lampData.intensity:
            direction = 1
        else:
            direction = -1
        HW().set_brightness(start=lampData.intensity, end=bri,direction=direction,increment=incriment)
        lampData.intensity = bri
        return [{"bri:": lampData.intensity, "user": current_user.username}]
    else:
        return [{"error-01:": "Inoperable Device Status: "+lampData.status, "user": current_user.username}]

@router.post("/set_cct/")
async def set_lamp_CCT(current_user: User = Depends(get_current_active_user),cct: int = 5000):
    if lampData.status != "BUSY":
        lampData.cct = cct
        lampData.status = "IDLE"
        return [{"cct:": lampData.cct, "user": current_user.username}]
    else:
        return [{"error-01:": "Inoperable Device Status: "+lampData.status, "user": current_user.username}]


@router.get("/get_intensity/")
async def get_intensity(current_user: User = Depends(get_current_active_user)):
    bri = HW().get_brightness()
    return [{"INTENSITY:": bri, "user": current_user.username}]

@router.get("/get_cct/")
async def get_cct(current_user: User = Depends(get_current_active_user)):
    return [{"CCT:": lampData.cct, "user": current_user.username}] 

@router.get("/get_distance/")
async def get_distance(current_user: User = Depends(get_current_active_user),range: int = 1):
    if lampData.status != "BUSY":
        lampData.status = "BUSY"
        tof = HW().config["SENSOR_DATA"]["TOF"]
        als = HW().config["SENSOR_DATA"]["ALS"]
        if range == 1:
            timing = HW().config["SENSOR_DATA"]["TIMING"]["SHORT"]
        elif range == 3:
            timing = HW().config["SENSOR_DATA"]["TIMING"]["LONG"]
        else:
            timing = HW().config["SENSOR_DATA"]["TIMING"]["ALL"]
        try:
            distance = Sensor().get_distance_from_object(bus = tof["I2C_BUS"], address = tof["I2C_ADDRESS"],range = range,timing = timing)
        except ModuleNotFoundError:
            return [{"error-02:": "ModuleNotFoundError: "+HW().config["SENSOR_DATA"]["TOF"]["MODEL"], "user": current_user.username}]
        try:
            proximity = Sensor().get_proximity()
        except ModuleNotFoundError:
            return [{"error-02:": "ModuleNotFoundError: "+HW().config["SENSOR_DATA"]["ALS"]["MODEL"], "user": current_user.username}]
        lampData.status = "IDLE"
        return [{"DISTANCE:": distance, "PROXIMITY": proximity, "user": current_user.username,"status:": lampData.status}]
    else:
        return [{"error-01:": "Inoperable Device Status: "+lampData.status, "user": current_user.username}]

@router.get("/get_ambient_light/")
async def get_ambient_light(current_user: User = Depends(get_current_active_user)):
    try:
        al = Sensor().get_ambient_light()
        return [{"AMBIENT_LIGHT:": al, "user": current_user.username}]
    except ModuleNotFoundError:
        return [{"error-02:": "ModuleNotFoundError: "+HW().config["SENSOR_DATA"]["ALS"]["MODEL"], "user": current_user.username}]