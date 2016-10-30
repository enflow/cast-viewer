import configparser
import os.path
import random
import string

def get_player_identifier():
    return get_config()['player']['identifier']

def get_config():
    config = configparser.ConfigParser()

    if not os.path.isfile(get_config_file()):
        config['player'] = {'identifier': generate_player_identifier()}

        with open(get_config_file(), 'w') as config_file:
            config.write(config_file)

    config.read(get_config_file())
    return config

def get_config_file():
    return '/home/pi/cast-viewer.ini'

def generate_player_identifier():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
