import cv2
import numpy as np
import time
import csv

from collections import OrderedDict

from src.utils import get_one_image, FPS
from src.ipcamera import IpCamera, IpCameraManager
from src.model.MobileNetSSD.detectionV2 import Detector
from src.centroidtracker import CentroidTracker
from src.model.FaceNet.recognition import face_match

CLOSER = 0.7 # Distance allowed to trust the face_match

class Experiment:
    def __init__(self):

        self.cameras = IpCameraManager()
        self.cameras.load("/Users/lucreveyron/Documents/SCN/scn/config/camera_config.toml")
        self.cameras.start_capture()
        self.camera_list = []

        for camera in self.cameras.return_list():
            self.camera_list.append(camera)

        self.detector = Detector()
        self.tracker = CentroidTracker()

        # Save info from all cameras
        self.frames = []

    def update_fuse(self):
        self.frames = []
        for camera in self.camera_list:
			# Pool the next frame 
            self.frames.append(self.cameras.return_specific_frame(camera))

        main_frame = get_one_image(self.frames)

        # compute orginal frame centers
        list_center = get_center(main_frame,len(self.frames))
        # Compute bounding box 
        _, bounding_box = self.detector.detect(main_frame)
        #print("bounding box:", bounding_box)
        # Label each bounding box with it's original frame
        labelled_box = get_box_label(bounding_box,list_center)
        # identify each person on the bounding box
        labelled_person = []
        # Try to recognize the person
        for box, label in labelled_box:
            img = main_frame
            result = face_match(img[box[1]:box[3],box[0]:box[2]],'/Users/lucreveyron/Documents/SCN/scn/model/FaceNet/finetune/data.pt')
            if result[0] is not None and result[1] > CLOSER:
                # Define the name of the person
                labelled_person.append([result[0],label])
        main_frame = draw_box(main_frame,bounding_box)
        return main_frame, labelled_person


def get_center(main_frame, nb_frames):
    frame_height = main_frame.shape[0]/nb_frames
    frame_width = main_frame.shape[1]

    list_center = []

    for index in range(nb_frames):
        list_center.append([frame_width/2,(frame_height/2)*(1+2*index)])

    return list_center

def get_box_label(rects,list_center):

    #print("box :",rects)
    #print("camera center:", list_center)

    labelled_box = []
    inputCentroids = np.zeros((len(rects), 2), dtype="int")
    # loop over the bounding box rectangles
    for (i, (startX, startY, endX, endY)) in enumerate(rects):
        # use the bounding box coordinates to derive the centroid
        cX = int((startX + endX) / 2.0)
        cY = int((startY + endY) / 2.0)
        index = closest_point((cX, cY), list_center)
        labelled_box.append([rects[i],index])

    return labelled_box

def closest_point(point, points):
    points = np.asarray(points)
    dist_2 = np.sum((points - point)**2, axis=1)
    return np.argmin(dist_2)

def draw_box(frame, boxes):
    
	for box in boxes:
		imgHeight, imgWidth, _ = frame.shape
		thick = int((imgHeight + imgWidth) // 900)

		cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]),
			(255, 0, 0), thick)

	return frame

def main():
    with open('measure/exp1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Exp", "fps","Person"])

        print("Measurement Start\n")
        exp1 = Experiment()
        t_end = time.time() + 60
        fps = FPS().start()

        while time.time() < t_end:
            fps.update()
            main_frame, output = exp1.update_fuse()
            #cv2.imshow("Display", main_frame)
            #print(output)
            fps.stop()
            writer.writerow([time.time(), fps.fps(),output])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    print("Measurement finish\n")

if __name__ == "__main__":
    main()




