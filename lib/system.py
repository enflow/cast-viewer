import requests
import re
import pytz
import sys
import sh
import os
import netifaces
import socket
import math
from datetime import timedelta, datetime
from pythonwifi.iwlibs import Wireless

def get_status():
    throttled = get_throttled()

    return {
        'now': str(datetime.now()),
        'version': get_git_tag(),
        'throttled': throttled,
        'is_under_voltage': is_under_voltage(throttled),
        'temp': vcgencmd('measure_temp').rstrip().replace('temp=', ''),
        'firmware': vcgencmd('version').split('\n'),
        'cec': get_cec(),
        'load': os.getloadavg(),
        'uptime': get_uptime(),
        'ips': get_ips(),
        'disk': get_disk(),
        'zerotier': get_zerotier_identity(),
        'wifi': get_wifi()
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

def get_ips():
    ips = {}
    for interface in netifaces.interfaces():
        ips[interface] = get_ip_by_interface(interface)
    return ips

def get_ip_by_interface(interface):
    try:
        ips = netifaces.ifaddresses(interface)
    except ValueError:
        return
    for k in ips.keys():
        ip = ips[k][0].get('addr', False)
        if ip:
            try:
                socket.inet_aton(ip)
                return ip
            except socket.error:
                pass
    return

def get_disk():
    disk = os.statvfs("/")
    capacity = disk.f_bsize * disk.f_blocks
    available = disk.f_bsize * disk.f_bavail
    used = disk.f_bsize * (disk.f_blocks - disk.f_bavail)
    return {
        'used': math.floor(used/1.048576e6),
        'available': math.floor(available/1.048576e6),
        'capacity': math.floor(capacity/1.048576e6)
    }

def hostname():
    hostname = socket.gethostname()

    if hostname == 'raspberrypi':
        raise RuntimeError('Hostname still is set to the default "raspberrypi". Unable to identiy with that.')

    return hostname

def api_url():
    return 'https://cast.enflow.nl/api/v1/player/{0}'.format(hostname())

def user_agent():
    return 'enflow-cast-viewer/{0}'.format(get_git_tag())

def get_zerotier_identity():
    return open('/var/lib/zerotier-one/identity.public').read().split(':')[0];

def get_wifi():
    if not get_ip_by_interface('wlan0'):
        return None

    wifi = Wireless('wlan0')
    aq = wifi.getQualityAvg()

    return {
        'essid': wifi.getEssid(),
        'frequency': wifi.getFrequency(),
        'quality': aq.quality,
        'signal': aq.siglevel,
        'noise': aq.nlevel
    }
