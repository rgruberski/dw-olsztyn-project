from imutils.video import VideoStream
import imutils
import cv2
import face_recognition

import time
from datetime import datetime


# from video_sources import Weeb, OtherChannel
from video_functions import *


# load detector model
net = cv2.dnn.readNetFromCaffe(
    "face_detector_model/deploy.prototxt.txt", 
    "face_detector_model/res10_300x300_ssd_iter_140000.caffemodel"
)


# video sources urls
weeb_channels = []
other_channels = [
    # (
    #     "TVP INFO", 
    #     "https://sdt-epix7-54.tvp.pl/token/video/live/14812849/20200126/1369639068/d85cf8ba-1852-4b63-9b15-01d066d02978/tvpinfo.isml/tvpinfo-audio%3D96000-video%3D120000.m3u8"
    # ),
    (
        "TVP 1", 
        "https://stream-cdn-1.videostar.pl/3/amlst:basic/chunk_uqqie58vn_ctaudio_cfm4s_ridp0aa0br96000_cs790313081184_mpd.m4s"
        # "https://stream-cdn-1.videostar.pl/3/amlst:basic/chunk_uqqie58vn_ctvideo_cfm4s_rid$RepresentationID$_cinit_mpd.m4s"
    )
]
video_sources = vs_prepare_sources(
    weeb_channels=weeb_channels, 
    other_channels=other_channels
)


# video streams setup 
video_streams = vs_prepare_streams(video_sources)

 
# face encodings buffer with timestamp
encodings_buffer = []
buffer_timestamp = datetime.now()

# print(video_sources) ###
print(video_streams) ###
# breakpoint()


# main loop
while True:
    #release frames
    captured_frames = []

    # loop over the frames from the video stream
    for vs in video_streams: 
        frame, face_locations = vs_detect_faces(vs, net)
        if frame is None:
            continue
        captured_frames.append(frame)

        # # encode faces, compare with buffer and add unseen to buffer
        # if len(face_locations) > 0:
        #     encodings = face_recognition.face_encodings(frame, face_locations)
        #     encodings_compare = [
        #         face_recognition.compare_faces(encodings_buffer, encoding, tolerance=0.4) 
        #         for encoding 
        #         in encodings
        #     ]
            
        #     for encoding, compare in zip(encodings, encodings_compare):
        #         if True not in compare:
        #             encodings_buffer.append(encoding)

    # release buffer after 10 sec.
    buffer_time = datetime.now() - buffer_timestamp
    if buffer_time.total_seconds() > 10:
        # do_something_with_buffered_encodings_and_timestamp(vs["encodings_buffer"], vs["buffer_timestamp"])
        print("BUFFER:", buffer_time.total_seconds(), "sec.") # current buffer time
        print("ENCODINGS:", len(encodings_buffer) ) # current buffer time
        print("frame status:", [f is None for f in captured_frames])
        encodings_buffer = [] # release buffer
        buffer_timestamp = datetime.now() # reset buffer timer

    # slow down processing
    # time.sleep(0.5)
    
    #TODO verify frames status
    # print("frame status:", [f is None for f in captured_frames])
    dead_frame_counter = 0
    if True in [f is None for f in captured_frames]:
        print(dead_frame_counter, "DEAD FRAMES!")
        time.sleep(5)
        dead_frame_counter += 1
        if dead_frame_counter % 20 == 0:
            print("BRAK FOR A MOMENT......")
            time.sleep(10)
        continue

    # show the output frames as montage
    montage_size = int(np.ceil( (len(captured_frames)) / 2))
    montage = imutils.build_montages(
        image_list=captured_frames, 
        image_shape=(frame.shape[1], frame.shape[0]), 
        montage_shape=(montage_size, montage_size)
    )[0]
    cv2.imshow("Frame", montage)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
if use_youtube:
    vs.release()
else:
    vs.stop()
