""" Server that manage connection with the front-end
"""
"""
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from typing import List, Dict
import json
import cv2
import numpy as np
import time

from smart_camera import SmartCamera

app = FastAPI()

"""
"""
# Allow Cross-Origin Resource Sharing
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:9999",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

# Init. smart camera network
"""
scn = SmartCamera()
cameras = scn.return_camera_list()
camera_status = {}
camera_status["camera1"] = "Off"
camera_status["camera2"] = "Off"
camera_status["camera3"] = "Off"

def check_status():
    key = "camera"
    for index in range(len(cameras)):
        camera_status["camera"+str(index)] = "On"

"""
"""
# Send the status of each camera
@app.get("/status")
async def send_status():
    #check_status()
    #json_camera_status = json.dumps(camera_status)
    #return json_camera_status
    return {"camera1":"On","camera2":"Off","camera3":"On"}

if __name__ == '__main__':
	uvicorn.run("server:app", host="0.0.0.0", port=9999, reload=True)