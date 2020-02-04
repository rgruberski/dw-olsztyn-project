"""
Funtions preparing and updating video streams
"""
import numpy as np
import cv2
import imutils
import pickle
import time
from video_sources import *

from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as chrome_options


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


def wp_pilot_login(browser, wp_login, wp_password, cookies_file, wp_url):
    browser.get('https://pilot.wp.pl/login/')
    browser.implicitly_wait(10)
    print("\n[PILOT] INITIALIZING PILOT")

    # load cookies
    print(cookies_file)
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
        print("PRIVACY ELEMENT NOT FOUND!", e)

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
        print("LOGIN ELEMENT NOT FOUND!", e)

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
        print("PASSWORD ELEMENT NOT FOUND!", e)

    # submit element
    try:
        element_submit = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[4]/div[1]/div[3]/div[2]/div/div[1]/form/button')
            )
        )
        browser.execute_script("arguments[0].click();", element_submit)
    except Exception as e:
        print("SUBMIT ELEMENT NOT FOUND!", e)
    
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
        print("WATCH HERE ELEMENT NOT FOUND!", e)
    
    try:
        browser.set_window_size(1920,1080)
    except Exception as e:
        print("COULD NOT RESIZE!", e)

    # press play in case of no autoplay
    time.sleep(10)
    try:
        element_play = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'btnplaybig')
            )
        )
        element_play.click()
    except Exception as e:
        print("PLAY ELEMENT NOT FOUND!", e)
    
    # save cookies
    with open(cookies_file, 'wb') as file:
        pickle.dump(browser.get_cookies(), file)
    

def wp_detect_faces(browser, net):
    # clean up face locations for new frame
    face_locations = []

    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    # frame = Image.open(io.BytesIO(browser.find_element_by_xpath(
    #     '//*[@id="Player0"]/div/div[1]/video').screenshot_as_png
    # ))
    frame = browser.find_element_by_xpath(
        '//*[@id="Player0"]/div/div[1]/video'
    ).screenshot_as_png
    frame = np.frombuffer(frame, np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
    
        # keep face location in face_recognition format
        face_locations.append((startY, endX, endY, startX))

    return frame, face_locations