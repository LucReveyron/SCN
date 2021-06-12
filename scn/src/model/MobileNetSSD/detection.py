#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module that discribe loader for MobileNetSSD model
"""

import numpy as np 
import cv2

from src.model.FaceNet.recognition import face_match

class Detector:
	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class

	CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		"sofa", "train", "tvmonitor"]

	# initialize the consider set (class labels we care about and want
	# to count), the object count dictionary, and the frame  dictionary
	CONSIDER = set(["person"])
	objCount = {obj: 0 for obj in CONSIDER}

	def __init__(self,reco = True):
		print("[INFO] loading model...")
		# Path to model 
		self.model = 'src/model/MobileNetSSD/MobileNetSSD_deploy.caffemodel'
		self.prototxt = 'src/model/MobileNetSSD/MobileNetSSD_deploy.prototxt'
		self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
		self.Confidence = 0.2
		self.person_frame = []
		self.reco = reco

	def detect(self,frame):

		# resize the frame to have a maximum width of 400 pixels, then
		# grab the frame dimensions and construct a blob
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
			0.007843, (300, 300), 127.5)
		# pass the blob through the network and obtain the detections and
		# predictions
		self.net.setInput(blob)
		self.detections = self.net.forward()
		# reset the object count for each object in the CONSIDER set
		self.objCount = {obj: 0 for obj in self.CONSIDER}	

	def draw_contour(self,frame,w,h):
		# loop over the detections

		imgHeight, imgWidth, _ = frame.shape
		thick = int((imgHeight + imgWidth) // 900)

		for i in np.arange(0, self.detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = self.detections[0, 0, i, 2]
			# filter out weak detections by ensuring the confidence is
			# greater than the minimum confidence
			if confidence > self.Confidence:
				# extract the index of the class label from the
				# detections
				idx = int(self.detections[0, 0, i, 1])
				# check to see if the predicted class is in the set of
				# classes that need to be considered
				if self.CLASSES[idx] in self.CONSIDER:
					# increment the count of the particular object
					# detected in the frame
					self.objCount[self.CLASSES[idx]] += 1

					# compute the (x, y)-coordinates of the bounding box
					# for the object
					box = self.detections[0, 0, i, 3:7] * np.array([w, h, w, h])
					(startX, startY, endX, endY) = box.astype("int")

					# Save part of the frame corresponding to a person
					self.person_frame.append(frame[startY:endY,startX:endX])

					# try to recongize the person
					name = None
					if self.person_frame[-1] is not None and self.reco is True:
						result = face_match(self.person_frame[-1],'/Users/lucreveyron/Documents/SCN/scn/model/FaceNet/finetune/data.pt')
						name = result[0]

					# draw the bounding box around the detected object on
					# the frame
					cv2.rectangle(frame, (startX, startY), (endX, endY),
						(255, 0, 0), thick)

					if name == None:
						cv2.putText(frame, self.CLASSES[idx], (startX, startY - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)
					else:
						cv2.putText(frame, name, (startX, startY - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)

		# draw the object count on the frame
		label = ", ".join("{}: {}".format(obj, count) for (obj, count) in
			self.objCount.items())
		cv2.putText(frame, label, (10, h - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)

		return frame

	def print_person(self):
		
		if len(self.person_frame) == 0:
			return None
		else:
			return self.person_frame[-1]




