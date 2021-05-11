""" Measure the variation of FPS function of detection and recogniction running
"""
import time
import csv
import cv2
from utils import resize, FPS
from ipcamera import IpCamera
#from model.MobileNetSSD.detection import Detector
from model.MobileNetSSD.detectionV2 import Detector
from model.FaceNet.recognition import face_match
from centroidtracker import CentroidTracker

def main():
	# Create csv file to store result
	with open('measure/fps_measure2.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["Exp", "fps"])
		print("Measurement Start\n")

		# Do test
		#writer = pure_video(writer)
		#writer = detection_only(writer)
		#writer = detection_and_recogniction(writer)
		#writer = recogniction_only(writer)
		writer = all(writer)

	print("Measurement finish\n")

def pure_video(writer):
	
	t_end = time.time() + 30
	cam1 = connection_manager()
	fps = FPS().start()
	
	while time.time() < t_end:
		frame = cam1.return_frames()
		fps.update()
		frame = resize(frame, width=400)
		cv2.imshow("Test", frame)
		fps.stop()
		writer.writerow([time.time(), fps.fps()])


	#writer.writerow(["Exp1", fps.fps()])
		
	
	return writer

def detection_only(writer):
	
	t_end = time.time() + 30
	cam1 = connection_manager()
	detector = Detector(reco = False)
	fps = FPS().start()
	
	while time.time() < t_end:
		frame = cam1.return_frames()
		fps.update()
		frame = detection_process(frame,detector)
		cv2.imshow("Test", frame)
		
		fps.stop()
		writer.writerow([time.time(), fps.fps()])
	return writer

def detection_and_recogniction(writer):
	
	t_end = time.time() + 30
	cam1 = connection_manager()
	detector = Detector(reco = True)
	fps = FPS().start()

	while time.time() < t_end:
		frame = cam1.return_frames()
		fps.update()
		frame = detection_process(frame,detector)
		cv2.imshow("Test", frame)
		fps.stop()
		writer.writerow([time.time(), fps.fps()])

	return writer

def recogniction_only(writer):

	t_end = time.time() + 30
	cam1 = connection_manager()

	fps = FPS().start()

	while time.time() < t_end:
		frame = cam1.return_frames()
		fps.update()
		result = face_match(frame,'/Users/lucreveyron/Documents/SCN/scn/model/FaceNet/finetune/data.pt')
		cv2.imshow('test', frame)
		fps.stop()
		writer.writerow([time.time(), fps.fps()])

	return writer

def all(writer):


	t_end = time.time() + 60
	cam1 = connection_manager()
	detector = Detector()
	tracker = CentroidTracker()

	fps = FPS().start()

	while time.time() < t_end:
		frame = cam1.return_frames()
		fps.update()
		frame, bounding_box = detector.detect(frame)
		if bounding_box:

			people, boxes = tracker.update(bounding_box)
		cv2.imshow('test', frame)
		fps.stop()
		writer.writerow([time.time(), fps.fps()])

	return writer

def connection_manager():
	# Select the correct procedure to receive the frames for the cameras

	adress = '192.168.1.31'
	user = 'Smartcap1'
	password = 'ProjectSCN2021'
	cam1 = IpCamera()
	cam1.add_all(adress,user,password)
	cam1.capture()

	return cam1

def detection_process(frame,detector):
	# Process to detect human presence on the frames
	# resize the frame to have a maximum width of 400 pixels, then
	# grab the frame dimensions and construct a blob
	frame = resize(frame, width=400)
	(h, w) = frame.shape[:2]

	detector.detect(frame)

	frame = detector.draw_contour(frame,w,h)

	return frame


if __name__ == "__main__":
    main()
