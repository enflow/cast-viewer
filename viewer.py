#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from os import path, getenv, utime
from random import shuffle
from time import sleep
from json import load as json_load
from websocket_server import WebsocketServer
from threading import Thread
from lib.system import is_under_voltage
from lib.utils import file_get_contents
import logging
import sh
import sys
import os
import urllib
import socket
import json
import rollbar

from lib.downloader import Downloader
from lib.scheduler import Scheduler

__author__ = "Enflow (original by WireLoad Inc)"
__copyright__ = "Copyright 2012-2016, WireLoad Inc"
__license__ = "Dual License: GPLv2 and Commercial License"

EMPTY_BROADCAST_DELAY = 10  # secs

browser = None
downloader = None
server = None

CWD = None
HOSTNAME = None

def load_browser():
    global browser
    logging.info('Loading browser...')

    if browser:
        logging.info('killing previous browser %s', browser.pid)
        browser.process.kill()

    command = sh.Command('chromium-browser')
    browser = command('--kiosk', '--incognito', '--no-first-run', '--disable-translate', '--system-developer-mode', 'file://' + CWD + '/www/player.html?debug=' + ("1" if DEBUGGING else "0"), _bg=True)
    logging.info('Browser loaded. Running as PID %s. Waiting 5 seconds to start.', browser.pid)
    sleep(5);


def browser_template(template, params=[]):
    logging.debug('Browser template \'%s\' with params %s', template, params)
    browser_url('file://{0}/www/{1}.html?{2}'.format(CWD, template, urllib.urlencode(params, True)))


def browser_send(command):
    send = json.dumps(command);
    server.send_message_to_all(send)
    logging.info('sended %s', send)


def browser_url(url, force=False):
    global browser

    if browser is None or not browser.process.alive:
        logging.info('browser found dead, restarting')
        load_browser()

    browser_send({'action': 'open', 'url': url, 'force': force})


def browser_preload(slide):
    if slide is None:
        return

    url = get_slide_url(slide)

    browser_send({'action': 'preload', 'url': url})


def view_video(uri, duration):
    browser_template('blank')

    player_args = ['omxplayer', uri]
    player_kwargs = {'o': 'hdmi', '_bg': True, '_ok_code': [0, 124]}
    player_kwargs['_ok_code'] = [0, 124]

    if duration and duration != 'N/A':
        player_args = ['timeout', duration] + player_args

    run = sh.Command(player_args[0])(*player_args[1:], **player_kwargs)

    while run.process.alive:
        sleep(1)
    if run.exit_code == 124:
        logging.info('omxplayer timed out')


def broadcast_loop(scheduler):
    if scheduler.state == scheduler.STATE_NO_CONNECTION:
        browser_template('no_connection')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    if scheduler.state == scheduler.STATE_REQUIRES_SETUP:
        browser_template('setup', {'player_identifier': HOSTNAME})
        sleep(EMPTY_BROADCAST_DELAY)
        return

    if scheduler.state == scheduler.STATE_INTERNAL_SERVER_ERROR:
        browser_template('internal_server_error')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    slide = scheduler.next_slide()
    logging.debug(slide)

    if slide is None:
        browser_template('no_slides')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    type, load = slide['type'], get_slide_url(slide)

    logging.info('Showing slide %s (%s)', type, load)

    preloadableSlide = scheduler.slide_to_preload()

    if 'web' in type:
        browser_url(load)

        duration = int(slide['duration'])

        sleep(1)

        # load next slide in advanced
        browser_preload(preloadableSlide);

        sleep(duration - 1)
    elif 'video' in type:
        browser_preload(preloadableSlide);

        view_video(load, slide['duration'])
    else:
        logging.error('Unknown type %s', type)


def get_slide_url(slide):
    if 'hash' in slide:
        return downloader.get_path_for_slide(slide)

    return slide['url']


def setup():
    global CWD, HOSTNAME, DEBUGGING
    CWD = os.getcwd()
    HOSTNAME = socket.gethostname()
    DEBUGGING = os.path.isfile('/boot/debug')

    rollbar_token = file_get_contents('/boot/rollbar')
    logging.debug(rollbar_token)
    if rollbar_token:
        rollbar.init(rollbar_token, 'production')

    if HOSTNAME == 'raspberrypi':
        raise RuntimeError('Hostname still is set to the default "raspberrypi". Unable to identiy with that.')

    if DEBUGGING:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)


def websocket_server():
    global server
    server = WebsocketServer(13254, host='127.0.0.1')
    server.run_forever()


def main():
    global downloader

    setup()

    downloader = Downloader()
    scheduler = Scheduler(HOSTNAME)

    t = Thread(target=websocket_server)
    t.daemon = True
    t.start()

    if is_under_voltage():
        browser_template('under_voltage')
        sleep(3 if DEBUGGING else 60)

    logging.debug('Entering infinite loop.')
    while True:
        if scheduler.index is 0:
            if scheduler.fetch():
                browser_template('loading')
                downloader.download(scheduler.slides)

            logging.debug('Scheduler state: %s', scheduler.state)

        broadcast_loop(scheduler)


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception("Cast viewer crashed.")
        rollbar.report_exc_info()

        raise
