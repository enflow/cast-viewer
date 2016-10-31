#!/bin/bash -e

if [ "$HOSTNAME" = "raspberrypi" ]
then
    IDENTIFIER=$(cat /dev/urandom | tr -dc 'A-Z0-9' | fold -w 10 | head -n 1)

    echo $IDENTIFIER > /etc/hostname
    hostname $IDENTIFIER
    /etc/init.d/hostname.sh start

    sed -i "s/raspberrypi/$IDENTIFIER/g" /etc/hosts

    echo "Changed hostname to identifier $IDENTIFIER"
fi

exit 0
