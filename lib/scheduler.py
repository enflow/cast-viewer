# -*- coding: utf-8 -*-

import requests
import logging
import json
from lib.config import get_player_identifier
from lib.system import get_status

class Scheduler(object):
    STATE_OK='OK'
    STATE_REQUIRES_SETUP='REQUIRES_SETUP'
    STATE_NO_CONNECTION='NO_CONNECTION'
    STATE_EMPTY='EMPTY'

    def __init__(self, hostname):
        logging.debug('Scheduler init')
        self.slides = None
        self.index = 0
        self.counter = 0
        self.hostname = hostname
        self.state = self.STATE_NO_CONNECTION

    def fetch(self):
        logging.debug('Scheduler.fetch')

        try:
            status = get_status()
            print json.dumps(status)

            r = requests.get('https://cast.enflow.nl/api/v1/player/{0}'.format(self.hostname), {'status': json.dumps(status)})
            decoded_response = r.json()
            logging.debug('Status code %s with response %s', r.status_code, decoded_response);

            if r.status_code == 200:
                slides = decoded_response['broadcast']['slides'] if decoded_response['broadcast'] else []

                if slides == self.slides:
                    logging.debug('Broadcast response didn\'t change')
                    return

                self.update_slides(slides)

                return True if slides else None
            elif r.status_code == 201:
                self.state=self.STATE_REQUIRES_SETUP
            else:
                self.state=self.STATE_NO_CONNECTION if not self.slides else self.STATE_OK
        except requests.exceptions.ConnectionError as e:
           logging.error('Loading from broadcast cache, ConnectionError: %s', e)

    def update_slides(self, slides):
        self.slides = slides;
        self.state = self.STATE_EMPTY if not self.slides else self.STATE_OK
        self.reload()

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

            if 'web' in slide['type'] or 'image' in slide['type']:
                return slide

        return None

    def reload(self):
        logging.debug('Scheduler.reload')

        self.counter = 0

        # Try to keep the same position in the play list. E.g. if a new slide is added to the end of the list, we
        # don't want to start over from the beginning.
        self.index = self.index % len(self.slides) if self.slides else 0

        logging.debug('reload done, count %s, counter %s, index %s', len(self.slides), self.counter, self.index)
