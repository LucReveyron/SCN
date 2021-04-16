import cv2
import numpy as np

from smart_camera import SmartCamera

def main():
	scn = SmartCamera()

	while True:
		scn.update()
		frame = scn.display()
		cv2.imshow("Display", frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	cv2.destroyAllWindows()

if __name__ == "__main__":
    main()