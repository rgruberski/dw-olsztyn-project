import cv2
import threading

class VideoGrabber():

    sources_urls = {
        "tvp:": "http://user:user@192.168.2.112:9981/stream/channel/28c32609c3e9143dff5dc1b0d16838cd?profile=mpeg",
        "polsat": "http://user:user@192.168.2.112:9981/stream/channel/a5f47e2442e9d19f43dafb7b51c686a2?profile=mpeg",
        "tvn": "http://user:user@192.168.2.112:9981/stream/channel/3679782872d6b7160b013fb8c0a9b393?profile=mpeg"
    }
    
    frames = {}

    def __init__(self, scaling_factor = 1): 
        self.scaling_factor = scaling_factor


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

            if self.scaling_factor > 1:
                
                height, width, _ =  frame.shape

                new_height = height / self.scaling_factor
                new_width = width / self.scaling_factor

                frame = cv2.resize(frame, (int(new_width), int(new_height)))

            self.frames[name] = frame


    def is_ready(self):
        return len(self.frames) == len(self.sources_urls)
