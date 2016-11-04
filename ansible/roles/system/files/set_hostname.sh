#!/bin/bash -e

if [ `hostname` = "raspberrypi" ]
then
    IDENTIFIER=$(tr -d -c "A-Z0-9" < /dev/urandom | head -c 10)

    echo "$IDENTIFIER" | tee /etc/hostname /boot/identifier.txt >/dev/null
    hostname $IDENTIFIER
    /etc/init.d/hostname.sh start

    sed -i "s/raspberrypi/$IDENTIFIER/g" /etc/hosts

    echo "Changed hostname to identifier $IDENTIFIER"
fi

exit 0
