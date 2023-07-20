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

from fastapi import Depends, FastAPI, APIRouter, HTTPException, status, Request, Query
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse,JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import uvicorn
import socket

from datetime import datetime, timedelta
from ...models.v1.security import Token, TokenData, User, UserInDB

from DIYson_lib.solarcycle import Solar
from DIYson_lib.Hardware import HW,Sensor
from DIYson_lib.auto import Auto

from .security import *
from .lamp import *

router = APIRouter(
    prefix="/v1/data",
    tags=["v1-Data"]
)

solar = Solar()
class Error_Message(BaseModel):
    message: str = "Error Message"
class Error_Detail(BaseModel):
    detail: str = "Error Detail"
class Success(BaseModel):
    value: float
    user: str

@router.get("/generate_cct/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Generate CCT for Sunrise, Noon and Sunset. Value Returns in Kelvin",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)
async def generate_cct_value(current_user: User = Depends(get_current_active_user)):
    cct_config = HW().config["LED_DATA"]["CCT"]
    min_cct = cct_config["MIN_CCT"]
    max_cct = cct_config["MAX_CCT"]
    srcct = cct_config["SRCCT"]
    ncct = cct_config["NCCT"]
    sscct = cct_config["SSCCT"]
    cct = solar.cct(mincct=min_cct,maxcct=max_cct,ssn=[srcct,ncct,sscct])

    return [{"cct:": cct, "user": current_user.username}]

@router.get("/generate_intensity/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Generate Solar Insolation (Intensity/Brightness). Value Returns as a Percentage",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)
async def generate_intenisty(current_user: User = Depends(get_current_active_user)):
    brightness_config = HW().config["LED_DATA"]["BRIGHTNESS"]
    brightness = solar.brightness(minbri=brightness_config["MIN_BRI"],maxbri=brightness_config["MAX_BRI"])
    return [{"value": brightness, "user": current_user.username}]

@router.get("/get_aim/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Generate the Age Intensity Multiplier given the user age. Value Returns as a float",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)
async def get_age_intensity_multiplier(current_user: User = Depends(get_current_active_user),age: int = 30):
    return [{"value": solar.age_intensity_multiplier(age), "user": current_user.username}]

@router.get("/get_sss_sr/",response_model=Success,
    responses={
        404: {"model": Error_Message, "description": Error_Detail},
        200: {
            "description": "Get the Sunrise and Sunset Times based on Locale.",
            "content": {
                "application/json": {
                    "example": Success
                }
            },
        },
    },)

async def get_sunrise_and_sunset(current_user: User = Depends(get_current_active_user)):
    return [{"SUNRISE:": solar.sunrise_sunset()[0], "SUNSET:": solar.sunrise_sunset()[1], "user": current_user.username}]

@router.get("/get_config/")
async def get_config(current_user: User = Depends(get_current_active_user)):
    return [{"CONFIG:": HW().config, "user": current_user.username}]