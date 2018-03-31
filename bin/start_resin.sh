#!/bin/bash

n=0
until [ $n -ge 5 ]
do
    SKIP_BACKUP=1 UPDATE_SELF=0 SKIP_WARNING=1 PRUNE_MODULES=1 BRANCH=next rpi-update && break
    n=$[$n+1]
    sleep 1
done

systemctl start X.service
systemctl start matchbox.service
systemctl start beamy.service

rm -rf /data/cast-downloads
mkdir -p /data/beamy-downloads

# By default docker gives us 64MB of shared memory size but to display heavy
# pages we need more.
umount /dev/shm
mount -t tmpfs shm /dev/shm
 
chown -R pi:pi /data
