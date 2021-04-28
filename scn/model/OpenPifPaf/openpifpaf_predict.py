import os
import cv2
import openpifpaf
import numpy as np

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

openpifpaf.show.Canvas.show = True
openpifpaf.show.Canvas.image_min_dpi = 200
os.environ['KMP_DUPLICATE_LIB_OK']='True'

class OpenPredict:
	def __init__(self):
		self.net_cpu, _ = openpifpaf.network.Factory(checkpoint='shufflenetv2k16', download_progress=False).factory()
		self.decoder = openpifpaf.decoder.factory([hn.meta for hn in self.net_cpu.head_nets])
		self.annotation_painter = openpifpaf.show.AnnotationPainter()

	def predict(self,frame):
		data = openpifpaf.datasets.NumpyImageList([frame])
		for image_tensor, _, meta in data:
			predictions = self.decoder.batch(self.net_cpu, image_tensor.unsqueeze(0))[0]

		return predictions




