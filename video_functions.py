"""
Funtions preparing and updating video streams
"""

import numpy as np
import cv2
import imutils
import pickle
from datetime import datetime
import time

import face_recognition

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chrome_options


def frame_compare_faces(encoding, known_encodings, known_names, tolerance=0.45):
    """
    Compare distances between encodings and return name of closest one 
    if distance is lower than tolerance
    """
    compare_distance = face_recognition.face_distance(known_encodings, encoding)
    closest_index = np.argsort(compare_distance)[0]
    closest_distance = compare_distance[closest_index]
    name = known_names[closest_index] if closest_distance < tolerance else "UNKNOWN"

    return name


def frame_detect_dnn(frame, net, min_confidence=0.7):
    # face locations list
    face_locations = []

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
        if confidence < min_confidence:
            continue

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # draw the bounding box of the face along with the associated
        # probability
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
    
        # keep face location in face_recognition format
        face_locations.append((startY, endX, endY, startX))
    
    return frame, face_locations


def wp_pilot_login(browser, wp_login, wp_password, cookies_file, wp_url):
    browser.get('https://pilot.wp.pl/login/')
    browser.implicitly_wait(10)
    print("[PILOT] INITIALIZING PILOT")

    # load cookies
    print("[PILOT] Loading cookies:", cookies_file)
    with open(cookies_file, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            browser.add_cookie(cookie)
    
    browser.refresh()
    time.sleep(5)

    # accept privacy
    try:
        element_accept = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[3]/button[1]")
            )
        )
        browser.execute_script("arguments[0].click();", element_accept)
    except Exception as e:
        print("[PILOT] Privacy element not found with E:", e)

    # login element
    try:
        element_login = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="pilot-login-email-field"]')
            )
        )
        browser.execute_script("arguments[0].click();", element_login)
        for key in wp_login:
            time.sleep(0.1)
            element_login.send_keys(key)
    except Exception as e:
        print("[PILOT] Login element not found with E:", e)

    # password element
    try:
        element_password = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="pilot-login-password-field"]')
            )
        )
        browser1.execute_script("arguments[0].click();", element_password)
        for key in wp_password:
            time.sleep(0.1)
            element_password.send_keys(key)
    except Exception as e:
        print("[PILOT] Password element not found with E:", e)

    # submit element
    try:
        element_submit = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[4]/div[1]/div[3]/div[2]/div/div[1]/form/button')
            )
        )
        browser.execute_script("arguments[0].click();", element_submit)
    except Exception as e:
        print("[PILOT] Submit element not found with E:", e)
    
    browser.get(wp_url)
    time.sleep(10)

    # watch here in case of other active players
    try:
        element_here = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="gatsby-focus-wrapper"]/div[3]/div[2]/div/div[2]/button[2]')
            )
        )
        browser.execute_script("arguments[0].click();", element_here)
    except Exception as e:
        print("[PILOT] Watch here element not found with E:", e)
    
    try:
        browser.set_window_size(1920,1080)
    except Exception as e:
        print("[PILOT] Could not set window size, E:", e)

    browser.refresh()

    # press play in case of no autoplay
    time.sleep(15)
    try:
        element_play = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'btnplaybig')
            )
        )
        element_play.click()
    except Exception as e:
        print("[PILOT] WARNING - PLAY ELEMENT NOT FOUND, E:", e)
    
    # save cookies
    with open(cookies_file, 'wb') as file:
        pickle.dump(browser.get_cookies(), file)
    

def wp_detect_faces(browser, net):
    # grab the frame from the threaded video stream and 
    # optionally resize it
    frame = browser.find_element_by_xpath(
        '//*[@id="Player0"]/div/div[1]/video'
    ).screenshot_as_png
    frame = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    # frame = imutils.resize(frame, width=400)

    # detect face locations
    frame, face_locations = frame_detect_dnn(frame, net)
    
    return frame, face_locations


def wp_screenshot_full(video_sources):
    for i, source in enumerate(video_sources):
        source.browser.save_screenshot(
            f"screenshots/vs_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )

