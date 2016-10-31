# -*- coding: utf-8 -*-

import requests
import logging
import downloader
from lib.config import get_player_identifier
from lib.utils import get_git_tag

class Scheduler(object):
    STATE_OK='OK'
    STATE_REQUIRES_SETUP='REQUIRES_SETUP'
    STATE_NO_CONNECTION='NO_CONNECTION'
    STATE_EMPTY='EMPTY'

    def __init__(self, hostname, downloader):
        logging.debug('Scheduler init')
        self.slides = None
        self.index = 0
        self.counter = 0
        self.hostname = hostname
        self.downloader = downloader
        self.state = self.STATE_NO_CONNECTION

    def fetch(self):
        logging.debug('Scheduler.fetch')

        try:
            r = requests.get('https://cast.enflow.nl/api/v1/player/{0}?version={1}'.format(self.hostname, get_git_tag()))
            decoded_response = r.json()
            logging.debug('Status code %s with response %s', r.status_code, decoded_response);

            if r.status_code == 200:
                if decoded_response == self.slides:
                    logging.debug('Broadcast response didn\'t change')
                    return None

                self.update_slides(decoded_response['broadcast']['slides'] if decoded_response['broadcast'] else [])
            elif r.status_code == 201:
                self.state=self.STATE_REQUIRES_SETUP
            else:
                self.state=self.STATE_NO_CONNECTION if not self.slides else self.STATE_OK

        except requests.exceptions.ConnectionError as e:
           logging.error('Loading from broadcast cache, ConnectionError: %s', e)

    def update_slides(self, slides):
        self.downloader.download(slides)

        self.slides = slides;
        self.state = self.STATE_EMPTY if not self.slides else self.STATE_OK
        self.reload()

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
