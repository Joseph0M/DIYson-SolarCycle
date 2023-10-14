#import all packages in PiZero/dyson_lib
from DIYson_lib.Serialization import serialize, deserialize
from DIYson_lib.Hardware import HW,als,tof,ps
from DIYson_lib.protocol import I2C
from DIYson_lib.protocol import OneWire
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse,JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional

from app.routes.api import router as api_router
import json
import os


OW = OneWire()
i2c = I2C()

with open(os.path.dirname(__file__) + '/DIYson_lib/config.json') as json_file: #load config.json
    config = json.load(json_file)
if OW.validate_serial(OW.get_serial()) and i2c.validate(): #validates hardware
    if config["LAMP_DATA"]["WIFI"]:
        ## API SETUP
        app = FastAPI(title="DIYson API by Joseph0M", description="A locally hosted API used to interface with the open-source DIYson Task Light by Steven Bennet. Software built by Joseph0M under the MIT License.", version="1.0.0-alpha3", openapi_url="/api/v1/openapi.json", redoc_url="/api/v1/redoc",)

        origins = ["http://localhost:8005"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.include_router(api_router)

        app.mount("/static", StaticFiles(directory="static"), name="static")


        @app.get("/docs", include_in_schema=False)
        async def swagger_ui_html(req: Request) -> HTMLResponse:
            root_path = req.scope.get("root_path", "").rstrip("/")
            openapi_url = root_path + app.openapi_url
            oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
            if oauth2_redirect_url:
                oauth2_redirect_url = root_path + oauth2_redirect_url
            return get_swagger_ui_html(
                openapi_url=openapi_url,
                title=app.title,
                oauth2_redirect_url=oauth2_redirect_url,
                init_oauth=app.swagger_ui_init_oauth,
                swagger_favicon_url="https://avatars.githubusercontent.com/u/75663305?v=4",
                swagger_ui_parameters=app.swagger_ui_parameters,
            )

        @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_oauth2_redirect_html()


        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title,
                redoc_js_url="/static/redoc.standalone.js",
                redoc_favicon_url="https://avatars.githubusercontent.com/u/75663305?v=4",
            )
        @app.route('/favicon.ico', include_in_schema=False)
        async def favicon():
            return FileResponse("https://avatars.githubusercontent.com/u/75663305?v=4")
        
    ## API SETUP END

        if __name__ == '__main__':
            uvicorn.run("main:app", host=str(config["SERVER_DATA"]["IP"]), port=int(config["SERVER_DATA"]["PORT"]), log_level="info", reload=True)
            print("running")