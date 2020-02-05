from video_sources import WPpilot
from video_functions import wp_pilot_login, wp_detect_faces, wp_screenshot_full

from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chrome_options

import numpy as np
import time
import pickle
import os
import imutils
import cv2


wp_login = ["dw.olsztyn.1@gmail.com", "dw.olsztyn1@wp.pl"]
wp_password = ["dwolsztyn1", "dwolsztyn1"]
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

        # remove this if not needed
        locations = []

        # loop over the frames from the video stream
        for source in video_sources:
            frame, face_locations = wp_detect_faces(source.browser, net)
            captured_frames.append(frame)
            
            # remove this
            locations.append(len(face_locations))
        # only checking detections
        print(locations)


        #TODO build face encodings
        #TODO push encodings to analyzer


        # show the output frames as montage
        montage_size = 2
        montage = imutils.build_montages(
            image_list=captured_frames, 
            image_shape=(frame.shape[1], frame.shape[0]), 
            montage_shape=(1, montage_size)
        )[0]
        cv2.imshow("Frame", montage)
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