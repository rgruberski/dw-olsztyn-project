import imutils
import cv2
import face_recognition
import time
from datetime import datetime
import pandas as pd
from video_functions import frame_detect_dnn, frame_compare_faces


# load known faces data
known_names = pd.read_pickle("dataset/president_faces_df.pickle")["name"].to_list()
known_encodings = pd.read_pickle("dataset/president_faces_df.pickle")["face_encodings"].to_list()

# load detector model
net = cv2.dnn.readNetFromCaffe(
    "face_detector_model/deploy.prototxt.txt", 
    "face_detector_model/res10_300x300_ssd_iter_140000.caffemodel"
)

# video sources urls
sources_urls = [
    "https://sdt-epix9-56.tvp.pl/token/video/live/46334064/20200213/1369639068/36a75d7f-78b2-43e1-9b95-ae6454b4c704/tvpinfo.isml/tvpinfo-audio%3D96000-video%3D1600000.m3u8"
]

# video streams setup 
video_streams = [cv2.VideoCapture(url) for url in sources_urls]
for i, vs in enumerate(video_streams):
    # check if source opened successfully
    if (vs.isOpened()== False): 
        print(f"[WARNING] Error opening video stream {i}")

# main loop
while True:
    try:
        #release frames
        captured_frames = []

        # loop over the frames from the video stream
        for vs in video_streams: 
            ret, frame = vs.read()
            if ret != True:
                continue

            # detect faces on frame
            frame, face_locations = frame_detect_dnn(frame, net, min_confidence=0.7)
            
            
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
            
            # keep processed frame for displaying
            captured_frames.append(frame)

        # show the output frames as montage
        montage_size = len(video_streams)
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

# cleanup
for vs in video_streams:
    vs.release()
cv2.destroyAllWindows()