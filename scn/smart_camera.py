#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module work as pipeline for camera smart tracking
"""

from collections import OrderedDict
import cv2

from utils import get_one_image
from ipcamera import IpCamera, IpCameraManager
from model.MobileNetSSD.detectionV2 import Detector
from centroidtracker import CentroidTracker
from model.FaceNet.recognition import face_match

CLOSER = 0.8 # Distance allowed to trust the face_match

class SmartCamera:
	def __init__(self):

		self.cameras = IpCameraManager()
		self.cameras.load("/Users/lucreveyron/Documents/SCN/scn/config/camera_config.toml")
		self.cameras.start_capture()

		self.detector = Detector()
		self.tracker = CentroidTracker()

		# Save info from all cameras
		self.frames = {}
		self.all_people = {}
		self.all_boxes = {}

		# Local to one per one camera
		self.people_tracked = {}
		self.boxes = {}
		for camera in self.cameras.return_list():
			self.people_tracked[camera] = OrderedDict()
			self.boxes[camera] = OrderedDict()

	def clear(self):
    	#clear the frames and boxes saved during previous update
		self.frames.clear()
		self.all_boxes.clear()

	def update(self):
		#print("[DEBUG] Current cameras list : ",self.cameras.return_list(), "\n")

		self.clear()

		for camera in self.cameras.return_list():

			if self.people_tracked[camera]:
				# Recover previous states : People tracked
				self.people_tracked[camera] = self.all_people[camera]

			# Pool the next frame 
			self.frames[camera] = self.cameras.return_specific_frame(camera)

			# Compute bounding box 
			self.frames[camera], bounding_box = self.detector.detect(self.frames[camera])
			if bounding_box:
				#print('bounding : ',len(bounding_box),'\n')
				people, self.boxes[camera] = self.tracker.update(bounding_box)
				#print('box : ',len(self.boxes),'\n')
				#print('people',len(people),'\n')

				for person_ID in people.keys():

					if person_ID not in self.people_tracked.keys():
						self.people_tracked[camera][person_ID] = None

				for person_ID in self.people_tracked[camera]:

					if self.people_tracked[camera][person_ID] == None and person_ID in self.boxes[camera].keys() :
						
						# Extrat person from the frame
						part_frame = self.frames[camera]
						part_frame = part_frame[self.boxes[camera][person_ID][1]:self.boxes[camera][person_ID][3],self.boxes[camera][person_ID][0]:self.boxes[camera][person_ID][2]]

						# Try to recognize the person
						result = face_match(part_frame,'/Users/lucreveyron/Documents/SCN/scn/model/FaceNet/finetune/data.pt')
						#print("[DEBUG] Match : ",result[1], "\n")
						if result[0] is not None and result[1] > CLOSER:
							# Define the name of the person
							self.people_tracked[camera][person_ID] = result[0]
				self.all_people[camera] = self.people_tracked[camera]
				self.all_boxes[camera] = self.boxes[camera]

	def return_camera_list(self):
		return self.cameras.return_list()

	def return_presence(self):
		people_detected = {}

		for camera in self.cameras.return_list():
			if camera in self.all_people.keys():
				people_detected[camera] = self.all_people[camera]
		return people_detected

	def return_frame(self,camera):
		if (camera in self.all_boxes.keys()) and (camera in self.all_people.keys()):
			frame = draw_box(self.frames[camera],self.all_boxes[camera], self.all_people[camera])
		else:
			frame = self.frames[camera]
		return frame
    			
	def display(self):
		list_frame = []

		for camera in self.cameras.return_list():
			
			if camera in self.all_people.keys() and camera in self.all_boxes.keys():	
				list_frame.append(draw_box(self.frames[camera],self.all_boxes[camera], self.all_people[camera]))
			else:
				list_frame.append(self.frames[camera])
		return get_one_image(list_frame)


def draw_box(frame, boxes, people):

	for index in boxes:
		imgHeight, imgWidth, _ = frame.shape
		thick = int((imgHeight + imgWidth) // 900)
		box = boxes[index]

		cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]),
			(255, 0, 0), thick)
		#print("[DEBUG] name is :",len(people))

		if index in people.keys():
			name = people[index]
		else:
			name = None

		if name == None:
			cv2.putText(frame, "Unknown", (box[0], box[1] - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)
		else:
			cv2.putText(frame, name, (box[0], box[1] - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)

	return frame




