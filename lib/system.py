import requests
import re
import pytz
import sys
import sh
import os
from datetime import timedelta

def get_status():
    throttled = get_throttled()
    return {
        'version': get_git_tag(),
        'throttled': throttled,
        'is_under_voltage': is_under_voltage(throttled),
        'temp': vcgencmd('measure_temp').rstrip().replace('temp=', ''),
        'firmware': vcgencmd('version').split('\n'),
        'cec': get_cec(),
        'load': os.getloadavg(),
        'uptime': get_uptime()
    }

def vcgencmd(command):
    return sh.vcgencmd(command).rstrip()

def get_throttled():
    return vcgencmd('get_throttled').replace('throttled=', '')

def is_under_voltage(throttled=None):
    if throttled is None:
        throttled = get_throttled()

    return throttled in ['0x50005', '0x50000']

def get_git_tag():
    commit = sh.git("rev-list", "--tags", "--max-count=1").rstrip()
    return sh.git("describe", "--tags", commit).rstrip()

def get_cec():
    return [i for i in sh.cec_client('-s', d=1, _in='pow 0', _ok_code=[0,1]).split('\n') if i][-1]

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return str(timedelta(seconds = uptime_seconds))
