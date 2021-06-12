import cv2
import numpy as np

from src.smart_camera import SmartCamera

def main():
	scn = SmartCamera()
	cameras = scn.return_camera_list()
	while True:
		scn.update()

		people_list = scn.return_presence()

		i = 1
		for camera in cameras:
			
			if camera in people_list.keys():

				for person in people_list[camera].values():
					if person != None:
						print("ROOM " + str(i) + " : \n")
						print(person)

			i += 1
		
		frame = scn.display()
		scn.return_presence()
		cv2.imshow("Display", frame)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows()

if __name__ == "__main__":
    main()