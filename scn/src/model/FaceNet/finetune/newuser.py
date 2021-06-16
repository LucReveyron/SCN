''' Class to implement smileV2.py functionnality
'''

import os
import cv2
from src.model.FaceNet.finetune.noise_generator import noisy

class saveUser:
	def __init__(self):
		self.username = ""
		self.counter = 0
		self.path = 'src/model/FaceNet/finetune/photos/'
		self.list_pictures = []

	def add(self,user):
		self.username = user
		self.path = self.path + self.username

		try:
		    os.mkdir(self.path)
		except OSError:
		    print ("Creation of the directory %s failed" % self.path)
		else:
		    print ("Successfully created the directory %s " % self.path)

	def save_picture(self,picture):
		self.list_pictures.append(picture)
		picture_name = "{}.jpg".format(self.counter)
		cv2.imwrite(os.path.join(self.path , picture_name), picture)
		self.counter += 1

	def augmentation(self):
		# Do data augmentation
		for img in self.list_pictures:
		    # rotation
		    list_rotation = [5,10,20,30,40] 

		    rows,cols, ch = img.shape

		    for rot in list_rotation:

		        M = cv2.getRotationMatrix2D((cols/2,rows/2),rot,1)
		        dst = cv2.warpAffine(img,M,(cols,rows))
		        img_name = "{}.jpg".format(self.counter)
		        cv2.imwrite(os.path.join(self.path , img_name), dst)
		        self.counter += 1
		    
		    # Add noise
		    noise_list = ["gauss", "s&p", "poisson", "speckle"]
		    
		    for noise in noise_list:
		        im_noisy = noisy(noise, img)
		        img_name = "{}.jpg".format(self.counter)
		        cv2.imwrite(os.path.join(self.path , img_name), im_noisy)
		        self.counter += 1
		    

	def name(self):
		return self.username

	def reset(self):
		self.path = './photos/'
		self.counter = 0
		self.list_pictures = []


	

