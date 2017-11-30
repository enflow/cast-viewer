#!/bin/sh

ping -c4 8.8.8.8 > /dev/null

if [ $? != 0 ]
then
  echo "No network connection, restarting wlan0"
  echo "$(date) Restarting Wifi " >> /home/pi/restart_wifi_status.log
  /sbin/ifdown 'wlan0'
  sleep 5
  /sbin/ifup --force 'wlan0'

  curl --data "type=update-failed&restarted-wifi=1" "https://cast.enflow.nl/api/v1/player/$HOSTNAME/report-failure"
fi