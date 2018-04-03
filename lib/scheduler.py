# -*- coding: utf-8 -*-

import requests
import logging
import json
from lib.system import user_agent
from lib.system import api_url

class Scheduler(object):
    STATE_OK='OK'
    STATE_REQUIRES_SETUP='REQUIRES_SETUP'
    STATE_NO_CONNECTION='NO_CONNECTION'
    STATE_INTERNAL_SERVER_ERROR='INTERNAL_SERVER_ERROR'
    STATE_EMPTY='EMPTY'

    def __init__(self):
        logging.debug('Scheduler init')
        self.slides = []
        self.index = 0
        self.counter = 0
        self.state = self.STATE_NO_CONNECTION

    def fetch(self):
        logging.debug('Scheduler.fetch')

        try:
            r = requests.get(api_url(), headers={'User-Agent': user_agent(), 'Accept': 'application/json'})
            decoded_response = r.json()
            logging.debug('Status code %s with response %s', r.status_code, decoded_response)

            if r.status_code == 200:
                slides = decoded_response['broadcast']['slides'] if decoded_response['broadcast'] else []

                self.state = self.STATE_EMPTY if not self.slides else self.STATE_OK

                if slides == self.slides:
                    logging.debug('Broadcast response didn\'t change')
                    return

                self.slides = slides
                self.reload()

                return True if slides else None
            elif r.status_code == 201:
                self.state=self.STATE_REQUIRES_SETUP
            elif r.status_code == 500:
                self.state=self.STATE_INTERNAL_SERVER_ERROR if not self.slides else self.STATE_OK
            else:
                self.state=self.STATE_NO_CONNECTION
        except requests.exceptions.SSLError as e:
           # pff
           # todo: rewrite to check the time trough dbus: https://github.com/resin-io-playground/resin-python-ntp-dbus/blob/master/ntptest.py
           logging.error('SSL error when loading broadcast. This is possibly due to a out-of-sync unit. Will "crash" for now but will ensure a valid state: %s', e)
           raise SystemExit('SSL error, possibly time is not synced yet')
        except requests.exceptions.ConnectionError as e:
           logging.error('Loading from broadcast cache, ConnectionError: %s', e)

    def next_slide(self):
        if not self.slides:
            return None

        idx = self.index
        self.index = (self.index + 1) % len(self.slides)
        logging.debug('get_next_slide counter %s returning slide %s of %s', self.counter, idx + 1, len(self.slides))
        self.counter += 1
        return self.slides[idx]

    def slide_to_preload(self):
        if not self.slides:
            return None

        for x in range(0, len(self.slides)):
            idx = (self.index + x) % len(self.slides)
            slide = self.slides[idx]

            return slide

        return None

    def reload(self):
        logging.debug('Scheduler.reload')

        self.counter = 0

        # Try to keep the same position in the play list. E.g. if a new slide is added to the end of the list, we
        # don't want to start over from the beginning.
        self.index = self.index % len(self.slides) if self.slides else 0

        logging.debug('reload done, count %s, counter %s, index %s', len(self.slides), self.counter, self.index)
