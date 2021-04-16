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

CLOSER = 0.2 # Distance allowed to trust the face_match

class SmartCamera:
	def __init__(self):

		self.cameras = IpCameraManager()
		self.cameras.load("/Users/lucreveyron/Documents/SCN/scn/config/ipcamera_list.txt")
		self.cameras.start_capture()

		self.detector = Detector()
		self.tracker = CentroidTracker()

		# Save info from all cameras
		self.frames = {}
		self.all_people = {}
		self.all_boxes = {}

		# Local to one per one camera
		self.people_tracked = OrderedDict()
		self.boxes = OrderedDict()

	def update(self):

		for camera in self.cameras.return_list():

			if self.people_tracked:
				# Recover previous states : People tracked
				self.people_tracked = self.all_people[camera]

			# Pool the next frame 
			self.frames[camera] = self.cameras.return_specific_frame(camera)

			# Compute bounding box 
			self.frames[camera], bounding_box = self.detector.detect(self.frames[camera])
			if bounding_box:
				print('bounding : ',len(bounding_box),'\n')
				people, self.boxes = self.tracker.update(bounding_box)
				print('box : ',len(self.boxes),'\n')
				print('people',len(people),'\n')

				for person_ID in people.keys():

					if person_ID not in self.people_tracked.keys():
						self.people_tracked[person_ID] = None

				for person_ID in self.people_tracked:

					if self.people_tracked[person_ID] == None and person_ID in self.boxes.keys() :
						
						# Extrat person from the frame
						part_frame = self.frames[camera]
						part_frame = part_frame[self.boxes[person_ID][1]:self.boxes[person_ID][3],self.boxes[person_ID][0]:self.boxes[person_ID][2]]

						# Try to recognize the person
						result = face_match(part_frame,'/Users/lucreveyron/Documents/SCN/scn/model/FaceNet/finetune/data.pt')
						if result[0] is not None and result[1] < CLOSER:
							# Define the name of the person
							self.people_tracked[person_ID] = result[0]
				self.all_people[camera] = self.people_tracked
				self.all_boxes[camera] = self.boxes

	def display(self):
		list_frame = []
		for camera in self.cameras.return_list():
			if self.all_people and self.all_boxes:
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
		name = people[index]

		if name == None:
			cv2.putText(frame, "Unknown", (box[0], box[1] - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)
		else:
			cv2.putText(frame, name, (box[0], box[1] - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)

	return frame



