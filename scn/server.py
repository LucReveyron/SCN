""" Server that manage connection with the front-end
"""

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from typing import List, Dict
import cv2
import numpy as np
import time

from src.smart_camera import SmartCamera

# Class to manage connection to each camera streams
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
    	for connection in self.active_connections:
    		await connection.send_text(data)

    async def send_frames(self, frames, websocket: WebSocket):
        await websocket.send(frames)

# init websocket manager and the smart camera network
manager = ConnectionManager()
scn = SmartCamera()
cameras = scn.return_camera_list()

class Map(BaseModel):
    rooms: Dict[str,List[str]]

app = FastAPI()

baseMap = {}
for camera in cameras:
    baseMap[camera] = []


async def return_base_presence():
    people_list = scn.return_presence()
    for camera in cameras:
        baseMap[camera] = []
        if camera in people_list.keys():
            for person in people_list[camera].values():
                if person != None:
                    baseMap[camera].append(person)
    return baseMap 

# Generate bytes from the camera frames
def generator(camera_id):
    while(True):
        img = scn.return_frame(camera_id)

        if np.shape(img) != ():

            (flag, encodedImage) = cv2.imencode(".jpg", img)
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')

@app.get("/app")
def read_index():
    return FileResponse("app.html")
"""
@app.get("/map")
async def create_item():
    scn.update()
    baseMap = await return_base_presence()
    #print(baseMap)
    return baseMap

@app.get("/stream")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # return StreamingResponse(generate())
    return StreamingResponse(generator(camera[0]), media_type="multipart/x-mixed-replace;boundary=frame")
"""

@app.websocket("/ws/map")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()

        while True:
            time.sleep(0.3)
            scn.update()
            baseMap = await return_base_presence()
            await websocket.send_json(baseMap)
    except WebSocketDisconnect:
        websocket.close()


@app.websocket("/ws/stream/{camera_id}")
async def websocket_stream(websocket: WebSocket, camera_id: str):
    await websocket.accept()

    while True:
        print("echo!\n")
        echo = await websocket.receive()
        await websocket.send(generator(camera_id))

#   except WebSocketDisconnect:
#        manager.disconnect(websocket)
#        await manager.broadcast(f"Camera #{camera_id} left")



if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=9999, reload=True)
