#!/usr/bin/env python
#from multiprocessing import Process
import time
import cv2
import serial
import numpy as np
import tensorflow.compat.v1 as tf
from flask import Flask, render_template, jsonify, request, Response
from py.detector import DetectorAPI

tf.disable_v2_behavior()
app = Flask(__name__)

global odapi
global engaged
# global ser
global feed
global feed_secondary
global serialOn
global fansEnabled
global doubleCam

serialOn = True
engaged = False
fansEnabled = False
doubleCam = True
MODEL_FOLDER = 'resources/'
# MODEL_NAME = './ssd_mobilenet_v3_large_coco_2020_01_14'
model_path = MODEL_FOLDER+'/frozen_inference_graph.pb'

odapi = DetectorAPI(path_to_ckpt=model_path)

if serialOn:
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM3'
    ser.open()
    if ser.is_open:
        print("serial connection initiated!")
    else:
        print("serial connection failed!")

cam_main = 1
cam_secondary = 2
feed = cv2.VideoCapture(cam_main, cv2.CAP_DSHOW)
feed_secondary = cv2.VideoCapture(cam_main, cv2.CAP_DSHOW)



@app.route('/')
def index():
    return render_template('index.html')

@app.route("/engageSwitch", methods=['POST'])
def engageSwitch():
    print(request.get_json())
    global engaged
    if request.method == 'POST':
        engaged = not engaged
        message = {'message': 'Switched!'}
        return jsonify(message)

@app.route("/enableFan", methods=['POST'])
def enableFans():
    print(request.get_json())
    global fansEnabled
    fansEnabled = not fansEnabled
    toggle_fan(fansEnabled)
    message = {'message': 'Switched!'}
    return jsonify(message)

@app.route("/left", methods=['GET'])
def left():
    global engaged, serialOn
    if request.method == 'GET' and not engaged and serialOn:
        message = {'message': 'Moved Left!'}
        shift_left();
        return jsonify(message)


@app.route("/right", methods=['GET'])
def right():
    global engaged, serialOn
    if request.method == 'GET' and not engaged and serialOn:
        message = {'message': 'Moved Right!'}
        shift_right();
        return jsonify(message)

@app.route("/video_feed")
def video_feed():
	return Response(run_fan(),
                 mimetype="multipart/x-mixed-replace; boundary=frame")


def shift_left():
    global serialOn
    if serialOn:
        global ser
        ser.write("l06\n".encode())


def shift_right():
    global serialOn
    if serialOn:
        global ser
        ser.write("r06\n".encode())

def toggle_fan(state):
    if state:
        app.logger.warning("Enable Fans")
        ser.write("x00\n".encode()) #enable fans
    else:
        app.logger.warning("Fans Disabled")
        ser.write("x01\n".encode()) #disable fans

def read_feed(feed_main, feed_secondary):
    global doubleCam
    r, img = feed_main.read()
    if not r:
        app.logger.error("Can't Read Image!")
        if doubleCam:
            r, img = feed_secondary.read()
    return (r, img)




def run_fan():
    global odapi
    global feed
    global feed_secondary
    global engaged
    global serialOn
    global fansEnabled

    if serialOn:
        global ser

    threshold = 0.6
    shift = (0, 0)
    prev_pos = (0, 0)
    current_pos = (0, 0)
    vel_check = False
    while True:
        r, img = read_feed(feed_secondary, feed)
        if not r:
            app.logger.error("Can't Read Image from secondary!")
            continue

        # img = cv2.resize(img, (1280, 720))
        height, width, channels = img.shape
        # img = cv2.resize(img, (width//4, height//4))
        # width, height = width//4, height//4
        boxes, scores, classes, num = odapi.processFrame(img)

        # Visualization of the results of a detection.
        # ser.write("x01\n".encode()) #disable fans

        if engaged:
            # app.logger.warning("Fans Enabled: ",fansEnabled)
            foundHuman = False
            for i in range(len(boxes)):
                # Class 1 represents human
                if classes[i] == 1 and scores[i] > threshold:
                    foundHuman = True
                    box = boxes[i]
                    center = ((box[1]+box[3])//2, (box[0]+box[2])//2)
                    # print(center)
                    radius = 50*(abs(box[1]-box[3]) + abs(box[0]-box[2]))//width
                    # print(radius)
                    cv2.circle(img, center, radius, (0, 0, 255), -1)
                    if vel_check:
                        prev_pos = (width//2, height//2)
                        calc_pos = center
                        shift = (calc_pos[0]-prev_pos[0],
                                calc_pos[1]-prev_pos[1])
                        
                        if shift[0] > 0:
                            if 100*abs(shift[0]/width) > 30:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted right by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("r05\n".encode())
                            if 100*abs(shift[0]/width) > 20:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted right by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("r03\n".encode())
                            elif 100*abs(shift[0]/width) > 7:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted left by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("r01\n".encode())
                        elif shift[0] < 0:
                            if 100*abs(shift[0]/width) > 30:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted right by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("l05\n".encode())
                            if 100*abs(shift[0]/width) > 20:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted left by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("l03\n".encode())
                            elif 100*abs(shift[0]/width) > 7:
                                prev_pos = current_pos
                                cv2.circle(img, prev_pos, 5, (255, 0, 0), -1)
                                current_pos = center
                                # print("human shifted left by",
                                #       100*abs(shift[0]/width), "%")
                                if serialOn:
                                    ser.write("l01\n".encode())
                    else:
                        prev_pos = center
                        current_pos = center
                        vel_check = True
            if not fansEnabled and foundHuman:
                toggle_fan(True)
                fansEnabled = True
            elif fansEnabled and not foundHuman:
                toggle_fan(False)
                fansEnabled = False

        # cv2.imshow("preview", img)
        r, encoded = cv2.imencode(".jpg", img)
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encoded) + b'\r\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
