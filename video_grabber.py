import cv2
import threading

class VideoGrabber():

    sources_urls = [
        "http://user:user@192.168.2.112:9981/stream/channel/3cf4f6ba84bc49cd959aa74a60edaf10?ticket=9CBA8B610E43E38F79A767B90D5A4534F9D26662&profile=mpeg",
        "http://user:user@192.168.2.112:9981/stream/channel/67d6df3bd7cd48ee41c11da1697f9c6c?ticket=67A745BA09456C3297F18AB2E13547013C1314E3&profile=mpeg",
        "http://user:user@192.168.2.112:9981/stream/channel/28c32609c3e9143dff5dc1b0d16838cd?ticket=0A4414C4AE44D119F4128E743BD2904B67EA5ED0&profile=mpeg"
    ]
    
    threads = []
    frames = {}

    @staticmethod
    def run():

        for url in VideoGrabber.sources_urls:
            pass
            # cap = cv2.VideoCapture(url)
