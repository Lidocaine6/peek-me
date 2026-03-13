from PIL import Image
import pystray
import threading
import logging
import time
import sys

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

    def run(self):
        logging.info('App running')
        self.tray_thread.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.icon.stop()
            sys.exit()

    def on_show(self):
        print('显示')

    def on_quit(self):
        logging.info('App quitting')
        self.icon.stop()
