from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import cv2
import base64
import asyncio
import numpy as np
from src.smart_camera import SmartCamera

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

# Generate bytes from the camera frames
def generator(id):
    while(True):
        camera_id = 'Smartcap' + str(id)
        img = scn.return_frame(camera_id)

        if np.shape(img) != ():

            (flag, encodedImage) = cv2.imencode(".jpg", img)
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')

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
    # Add response button !!
    ID = camID.id
    return camID

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

