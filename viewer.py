#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from os import path, getenv, utime
from random import shuffle
from time import sleep
from json import load as json_load
import logging
import sh
import sys
import os
import urllib
import socket

from lib.downloader import Downloader
from lib.scheduler import Scheduler

__author__ = "Enflow (original by WireLoad Inc)"
__copyright__ = "Copyright 2012-2016, WireLoad Inc"
__license__ = "Dual License: GPLv2 and Commercial License"

EMPTY_BROADCAST_DELAY = 10  # secs

current_browser_url = None
browser = None
chromix_too_server = None
downloader = None

CWD = None
HOSTNAME = None

def load_browser(url=None):
    global browser, current_browser_url
    logging.info('Loading browser...')

    if browser:
        logging.info('killing previous browser %s', browser.pid)
        browser.process.kill()

        if chromix_too_server:
            chromix_too_server.process.kill()

    if url is not None:
        current_browser_url = url

    # chromium-browser --kiosk --disable-translate --system-developer-mode --load-extension=/mnt/cast-viewer/extension_0_0_2/ --disable-session-crashed-bubble https://enflow.nl

    command = sh.Command('chromix-too-server')
    chromix_too_server = command(_bg=True)

    command = sh.Command('chromium-browser')
    browser = command('--disable-translate', '--system-developer-mode', '--load-extension=/mnt/cast-viewer/extension_0_0_2/', current_browser_url, _bg=True)
    logging.info('Browser loading %s. Running as PID %s.', current_browser_url, browser.pid)


def browser_send(command):
    if not (browser is None) and browser.process.alive:
        logging.debug('Send to chromix-too: %s', command)
        os.system('chromix-too {0}'.format(command) + ' &')
    else:
        logging.info('browser found dead, restarting')
        load_browser()


def browser_template(template, params=[]):
    logging.debug('Browser template \'%s\' with params %s', template, params)
    browser_url('file://{0}/templates/{1}.html?{2}'.format(CWD, template, urllib.urlencode(params, True)), force=True)


def browser_url(url, force=False):
    global current_browser_url

    if url == current_browser_url and not force:
        logging.debug('Already showing %s, reloading it.', current_browser_url)
    else:
        if current_browser_url:
            browser_send('close ' + current_browser_url)

        current_browser_url = url
        browser_send('open ' + current_browser_url)
        logging.info('current url is %s', current_browser_url)


def view_video(uri, duration):
    logging.debug('Displaying video %s for %s ', uri, duration)

    player_args = ['omxplayer', uri]
    player_kwargs = {'o': 'hdmi', '_bg': True, '_ok_code': [0, 124]}
    player_kwargs['_ok_code'] = [0, 124]

    if duration and duration != 'N/A':
        player_args = ['timeout', duration] + player_args

    run = sh.Command(player_args[0])(*player_args[1:], **player_kwargs)

    while run.process.alive:
        sleep(1)
    if run.exit_code == 124:
        logging.error('omxplayer timed out')


def broadcast_loop(scheduler):
    if scheduler.state == scheduler.STATE_NO_CONNECTION:
        browser_template('no_connection')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    if scheduler.state == scheduler.STATE_REQUIRES_SETUP:
        browser_template('setup', {'player_identifier': HOSTNAME})
        sleep(EMPTY_BROADCAST_DELAY)
        return

    slide = scheduler.get_next_slide()
    logging.debug(slide)

    if slide is None:
        browser_template('no_slides')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    type, load = slide['type'], slide['url']

    if 'download_hash' in slide:
        load = downloader.get_path_for_slide(slide)
        if not os.path.isfile(load):
            logging.info('Asset with download hash %s at %s is not available, skipping.', slide['download_hash'], slide['uri'])
            sleep(0.5)
            return

    logging.info('Showing slide %s (%s)', type, load)

    if 'web' in type or 'image' in type:
        browser_url(load)

        duration = int(slide['duration'])
        logging.info('Sleeping for %s', duration)
        sleep(duration)
    elif 'video' in type:
        view_video(load, slide['duration'])
    else:
        logging.error('Unknown type %s', type)

def setup():
    global CWD, HOSTNAME
    CWD = os.getcwd()
    HOSTNAME = socket.gethostname()

    if HOSTNAME == 'raspberrypi':
        raise RuntimeError('Hostname still is set to the default "raspberrypi". Unable to identiy with that.')

    # output logs to stdout
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def main():
    global downloader

    setup()

    downloader = Downloader()
    scheduler = Scheduler(HOSTNAME, downloader)

    logging.debug('Entering infinite loop.')
    while True:
        if scheduler.index is 0:
            scheduler.fetch()
            logging.debug('Scheduler state: %s', scheduler.state)

        broadcast_loop(scheduler)


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception("Viewer crashed.")
        raise
