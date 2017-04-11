#!/bin/bash -e

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

set -e
set -x

cd /home/pi/cast-viewer

git fetch --tags
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
CURRENT_TAG=$(git name-rev --tags --name-only $(git rev-parse HEAD))

if [ "$LATEST_TAG" = "$CURRENT_TAG" ]
then
    echo "No new update."
    exit 0
fi

git checkout $LATEST_TAG
chown -R pi:pi /home/pi/cast-viewer

ansible-playbook /home/pi/cast-viewer/ansible/site.yml --skip-tags system-upgrade

systemctl restart cast-viewer.service

set +x
set +e

echo "Update completed."
