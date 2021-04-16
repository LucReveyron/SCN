#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" The module receive the frames and apply person dectection,
	recogniction and tracking through all the network of IP cameras. 

	The information (frames, person ID and tracking position) are
	send to an html client.
"""

import cv2
import numpy as np

from utils import resize, get_one_image
from ipcamera import IpCamera, IpCameraManager
from model.MobileNetSSD.detection import Detector

from model.FaceNet.recognition import face_match


def main():
    
	cam1 = connection_manager()
	# Load model for person detection
	detector = Detector()

	while True:
		frame = cam1.return_frames()
		frame = detection_process(frame,detector)
		cv2.imshow("Test", frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	cv2.destroyAllWindows()

def connection_manager():
	# Select the correct procedure to receive the frames for the cameras

	# PROTO
	adress = '192.168.1.26'
	user = 'Smartcap1'
	password = 'ProjectSCN2021'
	cam1 = IpCamera()
	cam1.add_all(adress,user,password)
	cam1.capture()
	# PROTO

	return cam1

def detection_process(frame,detector):
	# Process to detect human presence on the frames

	# PROTO
	# resize the frame to have a maximum width of 400 pixels, then
	# grab the frame dimensions and construct a blob
	frame = resize(frame, width=400)
	(h, w) = frame.shape[:2]

	detector.detect(frame)

	frame = detector.draw_contour(frame,w,h) #, name)
	# PROTO
	#if face is not None:
		#cv2.imshow('face',face)

	return frame


if __name__ == "__main__":
    main()

