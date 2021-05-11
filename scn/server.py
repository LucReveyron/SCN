from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from typing import List, Dict
import cv2
import numpy as np

from smart_camera import SmartCamera

# init the smart camera network
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

def generator(camera_id):
    while(True):
        img = scn.return_frame(camera)
        print(img)
        if img is not None:
            npFrame = np.frombuffer(img, np.uint8)
            frame = cv2.imdecode(npFrame, cv2.IMREAD_COLOR)

            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encodedImage) + b'\r\n')

@app.get("/app")
def read_index():
    return FileResponse("app.html")

@app.get("/map")
async def create_item():
    scn.update()
    baseMap = await return_base_presence()
    print(baseMap)
    
    return baseMap

@app.get("/stream")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # return StreamingResponse(generate())
    return StreamingResponse(generator(camera[0]), media_type="multipart/x-mixed-replace;boundary=frame")

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=9999, reload=True)