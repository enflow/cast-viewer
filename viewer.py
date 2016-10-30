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

from lib.config import get_config, get_player_identifier
from lib.downloader import Downloader
from lib.scheduler import Scheduler

__author__ = "Enflow (original by WireLoad Inc)"
__copyright__ = "Copyright 2012-2016, WireLoad Inc"
__license__ = "Dual License: GPLv2 and Commercial License"

EMPTY_BROADCAST_DELAY = 10  # secs

WATCHDOG_PATH = '/tmp/cast-viewer.watchdog'

current_browser_url = None
browser = None
downloader = None

CWD = None

def watchdog():
    """Notify the watchdog file to be used with the watchdog-device."""
    if not path.isfile(WATCHDOG_PATH):
        open(WATCHDOG_PATH, 'w').close()
    else:
        utime(WATCHDOG_PATH, None)


def load_browser(url=None):
    global browser, current_browser_url
    logging.info('Loading browser...')

    if browser:
        logging.info('killing previous uzbl %s', browser.pid)
        browser.process.kill()

    if url is not None:
        current_browser_url = url

    # --config=-       read commands (and config) from stdin
    # --print-events   print events to stdout
    browser = sh.Command('uzbl-browser')(print_events=True, config='-', uri=current_browser_url, _bg=True)
    logging.info('Browser loading %s. Running as PID %s.', current_browser_url, browser.pid)

    browser_send('set ssl_verify = 1\nset show_status = 0\n')


def browser_send(command, cb=lambda _: True):
    if not (browser is None) and browser.process.alive:
        while not browser.process._pipe_queue.empty():  # flush stdout
            browser.next()

        browser.process.stdin.put(command + '\n')
        while True:  # loop until cb returns True
            if cb(browser.next()):
                break
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
        current_browser_url = url
        browser_send('uri ' + current_browser_url, cb=lambda buf: 'LOAD_FINISH' in buf)
        logging.info('current url is %s', current_browser_url)


def view_video(uri, duration):
    logging.debug('Displaying video %s for %s ', uri, duration)

    player_args = ['omxplayer', uri]
    player_kwargs = {'o': 'hdmi', '_bg': True, '_ok_code': [0, 124]}
    player_kwargs['_ok_code'] = [0, 124]

    if duration and duration != 'N/A':
        player_args = ['timeout', duration] + player_args

    run = sh.Command(player_args[0])(*player_args[1:], **player_kwargs)

    browser_template('black');

    while run.process.alive:
        watchdog()
        sleep(1)
    if run.exit_code == 124:
        logging.error('omxplayer timed out')


def broadcast_loop(scheduler):
    if scheduler.state == scheduler.STATE_NO_CONNECTION:
        browser_template('no_connection')
        sleep(EMPTY_BROADCAST_DELAY)
        return

    if scheduler.state == scheduler.STATE_REQUIRES_SETUP:
        browser_template('setup', {'player_identifier': get_player_identifier()})
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
    watchdog()

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
    global CWD
    CWD = os.getcwd()

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
    scheduler = Scheduler(downloader)

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
