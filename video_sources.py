"""
Classes for managing video sources
"""

class WPpilot:
    """
    Channels from https://pilot.wp.pl/, using selenium webdriver
    """
    def __init__(self, wp_login, wp_password, wp_cookies, wp_url):
        self.wp_login = wp_login,
        self.wp_password = wp_password,
        self.wp_cookies = wp_cookies,
        self.wp_url = wp_url
