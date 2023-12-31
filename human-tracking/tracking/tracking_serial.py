# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

import time
import cv2
import serial
import numpy as np
# import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name(
            'image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name(
            'detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name(
            'detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name(
            'detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name(
            'num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores,
                self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        # print("Elapsed Time:", end_time-start_time)

        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0, i, 0] * im_height),
                             int(boxes[0, i, 1]*im_width),
                             int(boxes[0, i, 2] * im_height),
                             int(boxes[0, i, 3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()


if __name__ == "__main__":
    MODEL_FOLDER = 'resources/'
    MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
    # MODEL_NAME = './ssd_mobilenet_v3_large_coco_2020_01_14'
    model_path = MODEL_FOLDER+MODEL_NAME+'/frozen_inference_graph.pb'
    odapi = DetectorAPI(path_to_ckpt=model_path)
    threshold = 0.6

    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM4'
    ser.open()
    if ser.is_open:
        print("serial connection initiated!")
    else:
        print("serial connection failed!")

    shift = (0, 0)
    prev_pos = (0, 0)
    current_pos = (0, 0)
    vel_check = False
    cam_no = 1
    feed = cv2.VideoCapture(cam_no)
    while True:
        r, img = feed.read()
        # img = cv2.resize(img, (1280, 720))
        height, width, channels = img.shape
        # img = cv2.resize(img, (width//4, height//4))
        # width, height = width//4, height//4
        boxes, scores, classes, num = odapi.processFrame(img)

        # Visualization of the results of a detection.
        pos_data = []
        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes[i]
                center = ((box[1]+box[3])//2, (box[0]+box[2])//2)
                # print(center)
                radius = 50*(abs(box[1]-box[3])+ abs(box[0]-box[2]))//width
                print(radius)
                cv2.circle(img, center, radius, (0, 0, 255), -1)
                if vel_check:
                    prev_pos = (width//2,height//2)
                    calc_pos = center
                    shift = (calc_pos[0]-prev_pos[0],
                             calc_pos[1]-prev_pos[1])
                    # print("prev", prev_pos,"current_pos", current_pos)
                    if shift[0] > 0:
                        if 100*abs(shift[0]/width) > 20:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted right by",
                                  100*abs(shift[0]/width), "%")
                            ser.write("r10\n".encode())
                        if 100*abs(shift[0]/width)>10:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted right by",
                                100*abs(shift[0]/width), "%")
                            ser.write("r03\n".encode())
                        elif 100*abs(shift[0]/width) > 2:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted left by",
                                  100*abs(shift[0]/width), "%")
                            ser.write("r01\n".encode())
                    elif shift[0] < 0:
                        if 100*abs(shift[0]/width) > 20:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted right by",
                                  100*abs(shift[0]/width), "%")
                            ser.write("l10\n".encode())
                        if 100*abs(shift[0]/width) > 10:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted left by",
                                100*abs(shift[0]/width), "%")
                            ser.write("l03\n".encode())
                        elif 100*abs(shift[0]/width) > 2:
                            prev_pos = current_pos
                            cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                            current_pos = center
                            print("human shifted left by",
                                  100*abs(shift[0]/width), "%")
                            ser.write("l01\n".encode())
                else:
                    prev_pos = center
                    current_pos = center
                    vel_check = True

        cv2.imshow("preview", img)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            cv2.destroyAllWindows
            break
