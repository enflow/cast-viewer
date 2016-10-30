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
import requests
import os
import urllib

from lib.utils import url_fails
from lib.config import get_player_identifier

__author__ = "Enflow (original by WireLoad Inc)"
__copyright__ = "Copyright 2012-2016, WireLoad Inc"
__license__ = "Dual License: GPLv2 and Commercial License"

EMPTY_BROADCAST_DELAY = 5  # secs

WATCHDOG_PATH = '/tmp/cast-viewer.watchdog'

current_browser_url = None
browser = None

CWD = None

class Scheduler(object):
    STATE_OK='OK'
    STATE_REQUIRES_SETUP='REQUIRES_SETUP'
    STATE_NO_CONNECTION='NO_CONNECTION'
    STATE_EMPTY='EMPTY'

    def __init__(self, *args, **kwargs):
        logging.debug('Scheduler init')
        self.slides = None
        self.index = 0
        self.counter = 0

    def fetch(self):
        logging.debug('Scheduler.fetch')

        try:
            r = requests.get('https://cast.enflow.nl/api/v1/player/{0}/broadcast'.format(get_player_identifier()))
            decoded_response = r.json()
            logging.debug('Status code %s with response %s', r.status_code, decoded_response);

            if r.status_code in xrange(200, 299):
                logging.debug(self.slides)

                if decoded_response == self.slides:
                    logging.debug('Broadcast response didn\'t change')
                    return None

                self.slides = decoded_response
                self.reload()

                self.state=self.STATE_EMPTY if not self.slides else self.STATE_OK
            elif r.status_code == 404:
                self.state=self.STATE_REQUIRES_SETUP
            else:
                self.state=self.STATE_NO_CONNECTION if not self.slides else self.STATE_OK

        except requests.exceptions.ConnectionError as e:
           logging.error('Loading from broadcast cache, ConnectionError: %s', e.args[0].reason.errno)

    def get_next_slide(self):
        logging.debug('Scheduler.get_next_slide')
        if not self.slides:
            return None

        idx = self.index
        self.index = (self.index + 1) % len(self.slides)
        logging.debug('get_next_slide counter %s returning slide %s of %s', self.counter, idx + 1, len(self.slides))
        self.counter += 1
        return self.slides[idx]

    def reload(self):
        logging.debug('Scheduler.reload')

        self.counter = 0

        # Try to keep the same position in the play list. E.g. if a new slide is added to the end of the list, we
        # don't want to start over from the beginning.
        self.index = self.index % len(self.slides) if self.slides else 0

        logging.debug('reload done, count %s, counter %s, index %s', len(self.slides), self.counter, self.index)


def watchdog():
    """Notify the watchdog file to be used with the watchdog-device."""
    if not path.isfile(WATCHDOG_PATH):
        open(WATCHDOG_PATH, 'w').close()
    else:
        utime(WATCHDOG_PATH, None)


def get_template(template, params=[]):
    return 'file://{0}/templates/{1}.html?{2}'.format(CWD, template, urllib.urlencode(params, True));


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
    logging.debug('Browser template %s with params %s', template, params)
    browser_url(get_template(template, params), force=True, cb=lambda buf: 'LOAD_FINISH' in buf)


def browser_url(url, cb=lambda _: True, force=False):
    global current_browser_url

    if url == current_browser_url and not force:
        logging.debug('Already showing %s, reloading it.', current_browser_url)
    else:
        current_browser_url = url
        browser_send('uri ' + current_browser_url, cb=cb)
        logging.info('current url is %s', current_browser_url)


def view_video(uri, duration):
    logging.debug('Displaying video %s for %s ', uri, duration)

    player_args = ['omxplayer', uri]
    player_kwargs = {'o': 'hdmi', '_bg': True, '_ok_code': [0, 124]}
    player_kwargs['_ok_code'] = [0, 124]

    if duration and duration != 'N/A':
        player_args = ['timeout', int(duration.split('.')[0])] + player_args

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
    elif scheduler.state == scheduler.STATE_REQUIRES_SETUP:
        browser_template('setup', {'player_identifier': get_player_identifier()})
        sleep(EMPTY_BROADCAST_DELAY)
    else:
        slide = scheduler.get_next_slide()
        logging.debug(slide)

        if slide is None:
            browser_template('no_slides')
            sleep(EMPTY_BROADCAST_DELAY)
        elif path.isfile(slide['url']) or not url_fails(slide['url']):
            type, url = slide['type'], slide['url']
            logging.info('Showing slide %s (%s)', type, url)
            watchdog()

            if 'web' in type:
                browser_url(url)

                duration = int(slide['duration'])
                logging.info('Sleeping for %s', duration)
                sleep(duration)
            elif 'video' in type:
                view_video(url, slide['duration'])
            else:
                logging.error('Unknown type %s', type)
        else:
            logging.info('Slide %s is not available, skipping.', slide['uri'])
            sleep(0.5)

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
    setup()

    scheduler = Scheduler()
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
