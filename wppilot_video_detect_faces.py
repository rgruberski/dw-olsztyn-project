from video_sources import WPpilot
from video_functions import wp_pilot_login, wp_detect_faces, wp_screenshot_full, frame_compare_faces

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_options

import pandas as pd
import numpy as np
import time
from datetime import datetime
import pickle
import os
import imutils
import cv2
import face_recognition


# load known faces data
known_names = pd.read_pickle("dataset/president_faces_df.pickle")["name"].to_list()
known_encodings = pd.read_pickle("dataset/president_faces_df.pickle")["face_encodings"].to_list()


# WPpilot credentials
with open("wp_credentials.pickle", "rb") as file:
    wp_login, wp_password = pickle.load(file)
wp_url = ['https://pilot.wp.pl/tv/#tvp-1-hd', 'https://pilot.wp.pl/tv/#tvn']
wp_cookies = ["cookies/wp_tvp1.pickle", "cookies/wp_tvn.pickle"]

# WPpilot sources
video_sources = [
    WPpilot(*i) 
    for i in zip(wp_login, wp_password, wp_cookies, wp_url)
]

# webdriver setup
options = chrome_options()
options.headless = True
chromedriver = os.path.abspath("chromedriver")

# opening browsers
for source in video_sources:
    source.browser = webdriver.Chrome(
        executable_path = chromedriver, 
        options = options
    )

# wp_pilot_login
for source in video_sources:
    wp_pilot_login(
        source.browser, 
        source.wp_login[0], 
        source.wp_password[0], 
        source.wp_cookies[0], 
        source.wp_url
    )

# control screenshots
wp_screenshot_full(video_sources)

# load detector model
net = cv2.dnn.readNetFromCaffe(
    "face_detector_model/deploy.prototxt.txt", 
    "face_detector_model/res10_300x300_ssd_iter_140000.caffemodel"
)

# main loop
while True:
    try:
        #release frames
        captured_frames = []

        # loop over the frames from the video stream
        for source in video_sources:
            frame, face_locations = wp_detect_faces(source.browser, net)
            captured_frames.append(frame)
            
        if len(face_locations) > 0:
            # build face encodings
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # compare encodings with known faces
            names = [
                frame_compare_faces(encoding, known_encodings, known_names) 
                for encoding in face_encodings
            ]

            # annotate face boxes with names
            for ((top, right, bottom, left), name) in zip(face_locations, names):
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(
                    frame, 
                    name, 
                    (left, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.75, 
                    (0, 255, 0), 2
                )
                #TODO do other stuff with frame
                if name != "UNKNOWN":
                    # do_other_stuff(frame)
                    # cv2.imwrite(f"screenshots/{datetime.now()} {name}.png", frame)
            

        # show the output frames as montage
        montage_size = 2
        montage = imutils.build_montages(
            image_list=captured_frames, 
            image_shape=(frame.shape[1], frame.shape[0]), 
            montage_shape=(montage_size, 1)
        )[0]
        cv2.imshow("Captured_frames", montage)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    except Exception as e:
        print(e)
        break

# do a bit of cleanup and close browsers
cv2.destroyAllWindows()
for source in video_sources:
    source.browser.close()
