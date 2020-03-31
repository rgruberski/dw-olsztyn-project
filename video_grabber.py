import cv2
import threading

class VideoGrabber():

    sources_urls = {
        "tvp": "http://user:user@192.168.2.131:9981/play/stream/channel/d9946f74d6bfd421745084ecd53a2ed6?profile=webtv-h264-aac-matroska",
        #"tvp": "https://rsdt-ols1-3.tvp.pl/token/video/live/47070364/20200331/1337698705/9d68b115-d231-4a45-9a6e-bb14c4a5de77/stream_0.m3u8",
        "polsat": "http://user:user@192.168.2.131:9981/play/stream/channel/d057275d05b42ff25a6812af2c2ec4ff?profile=webtv-h264-aac-matroska",
        "tvn": "http://user:user@192.168.2.131:9981/play/stream/channel/c7a8c1bd93e709bb58dab5f83a573e78?profile=webtv-h264-aac-matroska"
    }
    
    frames = {}

    def __init__(self, scaling_factor = 1, scaling_width = 0): 
        self.scaling_factor = scaling_factor
        self.scaling_width = scaling_width


    def run(self):

        for name, url in self.sources_urls.items():
            thread = threading.Thread(target=self.run_source_thread, args=(name, url), daemon = True)
            thread.start()

            print(f"Thread: {name} started")


    def run_source_thread(self, name, url):
        
        cap = cv2.VideoCapture(url)

        while True:

            ret, frame = cap.read()

            if frame is None:
                continue

            height, width, _ =  frame.shape

            if self.scaling_factor > 1:

                new_height = height / self.scaling_factor
                new_width = width / self.scaling_factor

                frame = cv2.resize(frame, (int(new_width), int(new_height)))

            elif self.scaling_width > 0:

                ratio = width / self.scaling_width

                new_height = height / ratio
                new_width = self.scaling_width

                frame = cv2.resize(frame, (int(new_width), int(new_height)))

            self.frames[name] = frame


    def is_ready(self):
        return len(self.frames) == len(self.sources_urls)
