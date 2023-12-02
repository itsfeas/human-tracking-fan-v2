import cv2
from os import walk
from os import remove

FRAME = 180
VIDEOPATH = "./videos/"
FRAMEPATH = "./frames/"

def list_files(mypath):
	f = []
	for (dirpath, dirnames, filenames) in walk(mypath):
		f.extend(filenames)
		break
	return(f)


file_list = list_files(VIDEOPATH)

i=0
for filename in file_list:
	vid = cv2.VideoCapture(VIDEOPATH + filename)
	vid.set(cv2.CAP_PROP_POS_FRAMES, FRAME)
	success, image = vid.read()
	cv2.imwrite(FRAMEPATH + "frame" + str(i) + ".png", image)
	i+=1