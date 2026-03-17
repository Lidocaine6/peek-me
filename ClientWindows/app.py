import threading
import logging
import time
import sys
import os

from PIL import Image
import pystray
import dotenv
import requests
from requests.exceptions import RequestException

from config import Config

class SpyApp:
    def __init__(self):
        logging.info('App created')
        tray_image = Image.open('icon.png')
        menu = pystray.Menu(
            pystray.MenuItem('显示', self.on_show),
            pystray.MenuItem('退出', self.on_quit),
        )
        self.icon = pystray.Icon(
            'spy_icon',
            tray_image,
            'SpyMeWindows',
            menu
        )
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        dotenv.load_dotenv()
        self.token = os.getenv('TOKEN')

    def run(self):
        logging.info('App running')
        self.tray_thread.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.icon.stop()
            sys.exit()

    def update_data(self, program_name, extra_data=''):
        try:
            response = requests.post(
                url=Config.server_addr + '/api/update',
                json={
                    'token': self.token,
                    'device_name': 'Windows',
                    'program_name': program_name,
                    'extra_data': extra_data,
                },
            )
            return response.json()
        except RequestException as e:
            self.handle_error(e)
    
    def handle_error(self, exception: str | Exception):
        pass

    def on_show(self):
        print('显示')

    def on_quit(self):
        logging.info('App quitting')
        self.icon.stop()
