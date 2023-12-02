import numpy as np
from scipy import ndimage as nd
from skimage.feature import hog
from imutils.object_detection import non_max_suppression
import skimage.segmentation

from matplotlib import pyplot as plt
import cv2
import math

DEBUG = True

filepath = "./frames/"

def resize(img):
	height, width, channels = img.shape
	dimensions = (width//4, height//4)
	img = cv2.resize(img, dimensions, interpolation = cv2.INTER_AREA)
	return img

def hog_filter(img, orient, radius):
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	fd, hog_image = hog(img_gray, orientations=8, pixels_per_cell=(radius, radius), cells_per_block=(1, 1), visualize=True)
	return hog_image

def detect(img):
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
	(rects, weights) = hog.detectMultiScale(img, winStride=(4, 4),
		padding=(8, 8), scale=1.05)

	# print(len(rects))
	# draw the original bounding boxes
	# for (x, y, w, h) in rects:
	# 	cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
	# apply non-maxima suppression to the bounding boxes using a
	# fairly large overlap threshold to try to maintain overlapping
	# boxes that are still people
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
	# draw the final bounding boxes
	for (xA, yA, xB, yB) in pick:
		cv2.rectangle(img, (xA, yA), (xB, yB), (0, 255, 0), 2)
	return img

if __name__ == '__main__' and DEBUG:
	file1 = "frame0.png"
	file1 = "frame1.png"
	file1 = "frame2.png"

	img = cv2.imread(filepath+file1)
	# img = resize(img)
	cv2.imshow("img", img)
	output_img = detect(img)
	# output_img = hog_filter(img, 8, 10)
	cv2.imshow("hog_filter", output_img)
	
	cv2.waitKey(0)
	cv2.destroyAllWindows