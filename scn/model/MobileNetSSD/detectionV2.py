#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module that discribe loader for MobileNetSSD model and pure detection
"""

import numpy as np 
import cv2

from utils import resize


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

	def __init__(self):
		print("[INFO] loading model...")
		# Path to model 
		self.model = 'model/MobileNetSSD/MobileNetSSD_deploy.caffemodel'
		self.prototxt = 'model/MobileNetSSD/MobileNetSSD_deploy.prototxt'
		self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
		self.Confidence = 0.2
		self.bounding_box = []


	def detect(self,frame):
		self.bounding_box = []
		# resize the frame to have a maximum width of 400 pixels, then
		# grab the frame dimensions and construct a blob
		frame = resize(frame, width=400)
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
			0.007843, (300, 300), 127.5)
		# pass the blob through the network and obtain the detections and
		# predictions
		self.net.setInput(blob)
		self.detections = self.net.forward()
		# reset the object count for each object in the CONSIDER set
		self.objCount = {obj: 0 for obj in self.CONSIDER}	

		# loop over the detections

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

					self.bounding_box.append([startX, startY, endX, endY])

		return frame, self.bounding_box

	def draw_contour(self,frame,name = None):

		imgHeight, imgWidth, _ = frame.shape
		thick = int((imgHeight + imgWidth) // 900)

		for box in self.bounding_box:
			# draw the bounding box around the detected object on
			# the frame
			cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]),
				(255, 0, 0), thick)

			if name == None:
				cv2.putText(frame, self.CLASSES[idx], (startX, startY - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)
			else:
				cv2.putText(frame, name, (startX, startY - 4), 0, 1e-3 * imgHeight, (255, 0, 0), thick//3)

		return frame
