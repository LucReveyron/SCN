from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import cv2
import re
import base64
import asyncio
import numpy as np
from typing import List
from src.smart_camera import SmartCamera
from src.model.FaceNet.finetune.newuser import saveUser

import uvicorn

# Init. smart camera network
camera_status = {}
camera_status["camera1"] = "true"
camera_status["camera2"] = "true"
camera_status["camera3"] = "true"

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:9999",
    "http://localhost:8080",
    "http://localhost:9999/status"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scn = SmartCamera()
cameras = scn.return_camera_list()

# ID of the camera we want to stream
ID = 0
class cameraID(BaseModel):
    id : int

# BaseModel for new user 
class newUser(BaseModel):
    user: str

userManager = saveUser()

class Picture(BaseModel):
    url: str

# Generate bytes from the camera frames
def current_frame(id):
    camera_id = 'Smartcap' + str(id)
    img = scn.return_frame(camera_id)
    if np.shape(img) != ():
        (_, encodedImage) = cv2.imencode(".jpg", img)

        return  bytearray((encodedImage))
    else:
        img = cv2.imread("/Users/lucreveyron/Documents/offline.jpg")
        (flag, encodedImage) = cv2.imencode(".jpg", img)
        return  bytearray((encodedImage))

def check_status():
    key = "camera"
    for index in range(len(cameras)):
        camera_status["camera"+str(1 + index)] = "false"

def check_presence():
    presence = scn.return_presence()
    print(presence)
    return presence

# Send the status of each camera
@app.get("/status")
async def send_status():
    check_status()
    return camera_status

# Send the name list of each camera of each camera
@app.get("/presence")
async def send_status():
    scn.update()
    presence = check_presence()
    return presence

# Set which camera to stream
@app.post("/choice")
async def select_stream(camID: cameraID):
    ID = camID.id
    return camID

# Add new user to database
@app.post("/username")
async def select_stream(newuser: newUser):
    # Object to manage creation of dateset for new user
    if(userManager.username != ""):
        print("augmented !\n")
        userManager.augmentation()
        userManager.reset()
        print("Reset...\n")

    userManager.add(newuser.user)
    return newuser

# Add picture to database
@app.post("/picture")
async def select_stream(img: Picture):
    # 1, information extraction
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", img.url, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")

    # 2, base64 decoding
    img_str = base64.urlsafe_b64decode(data)
    nparr = np.fromstring(img_str, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    userManager.save_picture(img_np)


@app.websocket("/ws/stream/{camID}")
async def websocket_endpoint(websocket: WebSocket, camID: int):
    try:
        await websocket.accept()
        isConnected = 1
        while(isConnected):
            scn.update()
            await websocket.send_bytes(current_frame(camID))
            data = await websocket.receive_text()
            if(data == '0'):
                isConnected = 0

        await websocket.close()
    except WebSocketDisconnect:
        websocket.close()

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True)

