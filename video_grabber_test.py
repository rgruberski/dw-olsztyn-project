import cv2
import imutils
from video_grabber import VideoGrabber

vg = VideoGrabber(4)

vg.run()

while True:

    if(vg.is_ready()):

        frames = vg.frames

        montage_frames = list(frames.values())

        montage = imutils.build_montages(
            image_list=montage_frames, 
            image_shape=(montage_frames[0].shape[1], montage_frames[0].shape[0]), 
            montage_shape=(3, 1)
        )[0]

        cv2.imshow("Captured_frames", montage)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
