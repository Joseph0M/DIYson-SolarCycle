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
    prefix="/v1/data",
    tags=["v1-Data"],
    responses={404: {"description": "Not found"}},
)
@router.get("/generate_cct/")
async def generate_cct_value(current_user: User = Depends(get_current_active_user)):
    cct = HW().config["LED_DATA"]["CCT"]
    print(cct)
    return [{"CCT VALUE:": Solar().cct(mincct=cct["MIN_CCT"],maxcct=cct["MAX_CCT"],ssn=[cct["SRCCT"],cct["NCCT"],cct["SSCCT"]]), "user": current_user.username}]
@router.get("/generate_intensity/")
async def generate_intenisty(current_user: User = Depends(get_current_active_user)):
    bri = HW().config["LED_DATA"]["BRIGHTNESS"]
    return [{"INTENISITY VALUE:": int(Solar().brightness(minbri=bri["MIN_BRI"],maxbri=bri["MAX_BRI"])), "user": current_user.username}]
@router.get("/get_aim/")
async def get_age_intensity_multiplier(current_user: User = Depends(get_current_active_user),age: int = 30):
    return [{"AIM:": Solar().age_intensity_multiplier(age), "user": current_user.username}]
@router.get("/get_sss_sr/")
async def get_sunrise_and_sunset(current_user: User = Depends(get_current_active_user)):
    return [{"SUNRISE:": Solar().sunrise_sunset()[0], "SUNSET:": Solar().sunrise_sunset()[1], "user": current_user.username}]
@router.get("/get_config/")
async def get_config(current_user: User = Depends(get_current_active_user)):
    return [{"CONFIG:": HW().config, "user": current_user.username}]