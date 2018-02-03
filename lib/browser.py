# -*- coding: utf-8 -*-

import sys
import os
import glob
import logging
import sh
import threading
import json
import urllib
from websocket_server import WebsocketServer
from time import sleep

class Browser(object):
    browser = None
    websocket_client = None
    websocket_server = None

    def __init__(self):
        logging.debug('Browser init')
        
        t = threading.Thread(target=self.start_websocket_server)
        t.daemon = True
        t.start()

    def start(self):
        logging.info('Loading browser...')

        if self.browser:
            logging.info('killing previous browser %s', browser.pid)
            self.browser.process.kill()

        self.browser = sh.chromium(
            '--kiosk',
            '--incognito',
            '--no-first-run',
            '--disable-translate',
            '--system-developer-mode',
            '--disable-hang-monitor',
            'file://' + os.getcwd() + '/www/player.html?debug=' + ("1" if True else "0"), 
            _bg=True
            )
        logging.info('Browser loaded. Running as PID %s. Waiting for websocket connection.', self.browser.pid)

        for i in range(1, 50):
            if self.websocket_client is None:
                break

            logging.debug("Waiting for websocket client %s", i)
            sleep(.5)

        # Ensure webpage is fully loaded
        sleep(5)

    def start_websocket_server(self):
        logging.debug('Running websocket server')

        self.websocket_server = WebsocketServer(13254, host='127.0.0.1')
        self.websocket_server.set_fn_new_client(self.websocket_client_joined)
        self.websocket_server.set_fn_client_left(self.websocket_client_left)
        self.websocket_server.run_forever()

    def websocket_client_joined(self, client, server):
        logging.debug("Chromium websocket client joined")
        print(client)

        self.websocket_client = client

    def websocket_client_left(self, client, server):
        logging.debug("Chromium closed websocket connection, restarting the browser in the next slide")

        self.websocket_client = None
        self.browser = None

    def template_url(self, template, params=[]):
        return '{1}.html#{2}'.format(os.getcwd(), template, urllib.urlencode(params, True)).rstrip('?')

    def template(self, name, params=[]):
        logging.debug('Browser template \'%s\' with params %s', name, params)

        self.url(self.template_url(name, params))

    def send(self, command):        
        if self.browser is None or not self.browser.process.alive:
            logging.info('Browser found dead, restarting')
            self.start()
        
        self.websocket_server.send_message_to_all(json.dumps(command))

    def url(self, url, force=False):
        self.send({'action': 'open', 'url': url, 'force': force})

    def preload(self, slide, url):
        if slide is None:
            return

        if 'video' or 'streaming' in slide['type']:
            url = self.template_url('blank')

        self.send({'action': 'preload', 'url': url})
