# -*- coding: utf-8 -*-

import pusherclient
import sh
import os
from lib.heartbeater import send_heartbeat

class Pusher(object):
    def __init__(self):
        self.pusher = pusherclient.Pusher('82341182465af8c47698', cluster='eu')
        self.pusher.connection.bind('pusher:connection_established', self.pusher_connected)
        self.pusher.connect()

    def event_reboot(self, data):
        os.system('sudo reboot')

    def event_connect_to_zerotier(self, data):
        os.system('sudo /usr/sbin/zerotier-cli join 17d709436cf23366')

    def event_send_heartbeat(self, data):
        send_heartbeat()

    def pusher_connected(self, data):
        channel = self.pusher.subscribe('KSXVBADTVP')
        channel.bind('reboot', self.event_reboot)
        channel.bind('connect_to_zerotier', self.event_connect_to_zerotier)
        channel.bind('send_heartbeat', self.event_send_heartbeat)
