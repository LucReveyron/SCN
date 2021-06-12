#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module that define IpCamera object, IpCameraManager and a function to read list
	of Ip camera
"""

import cv2
import toml

from src.cameravideostream import CameraVideoStream

class IpCamera:
	def __init__(self):
		self.ip_camera = {}

	def add_link(self, adress):
		self.ip_camera['adress'] = adress

	def add_username(self, username):
		self.ip_camera['username'] = username

	def add_password(self, password):
		self.ip_camera['password'] = password

	def add_all(self, adress, username, password):
		self.add_link(adress)
		self.add_username(username)
		self.add_password(password)

	def return_user(self):
		return self.ip_camera['username']

	def capture(self):
		# Connect to the ipcamera and capture the frames
		self.url = "rtsp://{user}:{passw}@{adress}/stream2".format(user = 
			self.ip_camera['username'], passw = self.ip_camera['password'], 
			adress = self.ip_camera['adress'])

		self.cvs = CameraVideoStream(src=self.url,name=self.return_user()).start()
		print("[INFO] Init. ",self.ip_camera['username'],"\n")

	def return_frames(self):
		return self.cvs.read()

class IpCameraManager:
	def __init__(self):
		self.camera_list = {}

	def add_ip_camera(self, ip_camera):
		# If ip_camera is a list of ip_camera we define camera_list as this list
		if len(ip_camera) == 1 :
			self.camera_list[ip_camera[-1].return_user()] = ip_camera[-1]
		else:
			for i in range(len(ip_camera)):
				self.camera_list[ip_camera[i].return_user()] = ip_camera[i]

	def load(self, file):
		ip_cameras = generate_ip_camera_from_toml(file)
		self.add_ip_camera(ip_cameras)
		print("[INFO] Camera list load \n")

	def start_capture(self):
		for ip_camera in self.camera_list:
			self.camera_list[ip_camera].capture()

	def remove_ip_camera(self, ip_camera):
		self.camera_list.pop(ip_camera.return_user())

	def return_list(self):
		return self.camera_list

	def return_nb_cameras(self):
		return len(self.camera_list)

	def return_specific_frame(self,username):
		return self.camera_list[username].return_frames()

	def return_frames(self):
		# Return a dictionnary of frames of each ip camera connected, key are the users
		frames = {}
		for camera in self.camera_list:
			frames[camera.return_user()] = camera.return_frames()

		return frames

def generate_ip_camera_from_txt(file):
	# read .txt file with list of ip cameras and build IpCamera object
	list_ip_cameras = []

	with open(file) as input_file:
		for line in input_file:
			list_ip_cameras.append(IpCamera())
			adress, username, password = (
				item.strip() for item in line.split(';', 3))

			list_ip_cameras[-1].add_all(adress, username, password)


	return list_ip_cameras

def generate_ip_camera_from_toml(file):
	# read .toml file with list of ip cameras and build IpCamera object
	list_ip_cameras = []

	dict_toml = toml.load(file)

	for key in dict_toml:
		list_ip_cameras.append(IpCamera())
		camera = dict_toml[key]
		adress = camera["ip"]
		username = camera["username"]
		password = camera["password"]
		list_ip_cameras[-1].add_all(adress, username, password)

	return list_ip_cameras


