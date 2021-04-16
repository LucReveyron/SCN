#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module that define classes to streams camera
	Almost take from : https://github.com/jrosebr1/imutils/blob/master/imutils/video/webcamvideostream.py 
"""

from threading import Thread
import cv2

class CameraVideoStream:
	def __init__(self, src=0, name="CameraVideoStream"):
		# initialize the video camera stream and read the first frame
		# from the stream
		print('[Info] Stream from:', name)

		self.stream = cv2.VideoCapture(src)

		(self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
		self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()

	def read(self):
		# return the frame most recently read
		return self.frame

	def change_res(self,res):
		# Set resolution
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
