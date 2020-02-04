import requests
import json

class WPpilot:
    """
    Channels from https://pilot.wp.pl/, using selenium webdriver
    """
    def __init__(self, wp_login, wp_password, wp_cookies, wp_url):
        self.wp_login = wp_login,
        self.wp_password = wp_password,
        self.wp_cookies = wp_cookies,
        self.wp_url = wp_url

class Weeb:
    """
    Channels list at: http://weeb.tv/channels/live
    """    
    def __init__(self, channel):
        self.channel = channel
        self.get_url()

    def get_url(self):
        channel = self.channel
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }
        weeb_api = "http://weeb.tv/api/htmlsetplayer"
        response = requests.get(weeb_api + f"&cid={channel}", headers=headers)
        response_data = response.json()
        try:
            response_data = [
                val 
                for val 
                in response_data.values() 
                if "playlist.m3u8" in str(val)
            ]
            self.url = response_data[0]
            print(f"[Weeb] CHANNEL: {channel}, URL: {self.url}")
        except Exception as e:
            print(f"[Weeb] ERROR: {e}, CHANNEL: {channel}")
            self.url = None


class OtherChannel:
    """
    Channels with known urls
    """
    def __init__(self, channel, url):
        self.channel = channel
        self.url = url
    
    # dummy method
    def get_url(self):
        pass