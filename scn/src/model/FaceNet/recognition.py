""" This module use MTCNN and resnet to recognize people on frames 
"""

import os
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image

MIN_SIZE = 10000 # To filter artefact from detection stage (too small images that cannot be usable)

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

def face_match(frame, data_path): # img_path= location of photo, data_path= location of data.pt 
    # getting embedding matrix of the given img
	img = frame
	face = None
	#print("[DEBUG] Check a none empty frame pass : size = ",img.size)

	if img.size > MIN_SIZE:
		face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability

	if face is not None:

		emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false
	    
		saved_data = torch.load(data_path) # loading data.pt file
		embedding_list = saved_data[0] # getting embedding data
		name_list = saved_data[1] # getting list of names
		dist_list = [] # list of matched distances, minimum distance is used to identify the person
	    
		for idx, emb_db in enumerate(embedding_list):
			dist = torch.dist(emb, emb_db).item()
			dist_list.append(dist)
	        
		idx_min = dist_list.index(min(dist_list))
		#face = face.detach().cpu().numpy()
		#face = face.transpose(1, 2, 0)
		return (name_list[idx_min], dist_list[idx_min])
	else:
		return (None,None)