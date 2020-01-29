"""
Funtions preparing and updating video streams
"""
import numpy as np
import cv2
import imutils
from video_sources import *


def vs_prepare_sources(weeb_channels=[], other_channels=[]):
    video_sources = \
        [Weeb(ch) for ch in weeb_channels] + \
        [OtherChannel(ch[0], ch[1]) for ch in other_channels]
    video_sources = [
        source 
        for source 
        in video_sources 
        if source.url is not None
    ]
    return video_sources


def vs_prepare_streams(video_sources):
    video_streams = [cv2.VideoCapture() for source in video_sources]
    for stream, source in zip(video_streams, video_sources):
        stream.open(source.url)
    return video_streams


def vs_detect_faces(vs, net):
    # clean up face locations for new frame
    face_locations = []

    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    success, frame = frame
    if not success:
        return None, face_locations
    frame = imutils.resize(frame, width=400)

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (400, 400)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))
    
    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence < 0.7:
            continue

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # draw the bounding box of the face along with the associated
        # probability
        # text = "{:.2f}%".format(confidence * 100)
        # y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
        # cv2.putText(frame, text, (startX, y),
        #     cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    
        # keep face location in face_recognition format
        face_locations.append((startY, endX, endY, startX))

    return frame, face_locations