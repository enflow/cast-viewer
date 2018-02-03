import requests
import re
import sys
import sh
import os
import subprocess
import netifaces
import socket
import math
import os
from datetime import timedelta, datetime
from pythonwifi.iwlibs import Wireless

def get_status():
    throttled = get_throttled()

    return {
        'now': str(datetime.now()),
        'throttled': throttled,
        'is_under_voltage': is_under_voltage(throttled),
        'temp': vcgencmd('measure_temp').rstrip().replace('temp=', ''),
        'firmware': vcgencmd('version').split('\n'),
        'cec': get_cec(),
        'load': os.getloadavg(),
        'uptime': get_uptime(),
        'ips': get_ips(),
        'disk': get_disk(),
        'wifi': get_wifi()
    }

def vcgencmd(command):
    try:
        return sh.vcgencmd(command, _timeout=3).rstrip()
    except sh.ErrorReturnCode:
        return ''

def get_throttled():
    return vcgencmd('get_throttled').replace('throttled=', '')

def is_under_voltage(throttled=None):
    if throttled is None:
        throttled = get_throttled()

    return throttled in ['0x50005', '0x50000']

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

def device_uuid():
    if "/mnt" in os.getcwd():
        return "DEBUGGG" # 7 chars

    return socket.gethostname().upper()

def api_url():
    return 'https://cast.enflow.nl/api/v1/player/{0}'.format(device_uuid())

def user_agent():
    return 'enflow-cast/{0}'.format(device_uuid())

def get_wifi():
    if not get_ip_by_interface('wlan0'):
        return None

    try:
        wifi = Wireless('wlan0')
        aq = wifi.getQualityAvg()

        return {
            'essid': wifi.getEssid(),
            'frequency': wifi.getFrequency(),
            'quality': aq.quality,
            'signal': aq.siglevel,
            'noise': aq.nlevel
        }
    except Exception as e:
        return str(e)
