import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from diyson_api.routes.api import router as api_router
import json

with open("DIYson/Firmware/diyson_api/lib/config.json") as json_file: #load config.json
    config = json.load(json_file)
if config["LAMP_DATA"]["WIFI"] == True:
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