import cv2
import numpy as np

from utils import resize, get_one_image
from ipcamera import IpCamera, IpCameraManager
from model.OpenPifPaf.openpifpaf_predict import OpenPredict


def main():
    
	cam1 = connection_manager()
	# Load model for person detection
	detector = OpenPredict()

	while True:
		frame = cam1.return_frames()
		prediction = detection_process(frame,detector)
		box = prediction[-1].bbox()
		#print(box)
		frame = draw_box(frame,box)
		cv2.imshow("Test", frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	cv2.destroyAllWindows()

def connection_manager():
	# Select the correct procedure to receive the frames for the cameras

	# PROTO
	adress = '192.168.1.31'
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

	prediction = detector.predict(frame)
	# PROTO
	#if face is not None:
		#cv2.imshow('face',face)

	return prediction

def draw_box(frame, box, name=None):


	imgHeight, imgWidth, _ = frame.shape
	thick = int((imgHeight + imgWidth) // 900)
	

	cv2.rectangle(frame, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
		(255, 0, 0), thick)




	return frame


if __name__ == "__main__":
    main()

