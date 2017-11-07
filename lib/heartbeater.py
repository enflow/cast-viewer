# -*- coding: utf-8 -*-

from lib.system import get_status
from lib.system import api_url
from lib.system import user_agent
import logging
import json
import threading
import requests
import socket
from random import randint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def send_heartbeat():
    threading.Timer(randint(45.0, 60.0), send_heartbeat).start()

    logging.debug('Sending heartbeat')

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    try:
        status = get_status()

        r = requests.post(api_url() + '/heartbeat', json=status, headers={'User-Agent': user_agent(), 'Accept': 'application/json'}, verify=False)

        if r.status_code is not 200:
            logging.error('Heartbeat: status code %s with response %s', r.status_code, r.text);
    except requests.exceptions.ConnectionError as e:
        logging.error('Unable to send heartbeat, ConnectionError: %s', e)
