#!/bin/bash -e

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

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

OUTPUT="$(ansible-playbook /home/pi/cast-viewer/ansible/site.yml --skip-tags system-upgrade 2>&1)"

if [ "$?" -ne "0" ]
then
    echo "Ansible playbook failed, checking out old tag $CURRENT_TAG"

    git checkout $CURRENT_TAG

    curl -v --data "type=update-failed&current_tag=$CURRENT_TAG&latest_tag=$LATEST_TAG&output=$OUTPUT" "https://cast.enflow.nl/api/v1/player/$HOSTNAME/report-failure"

    exit 1
fi

systemctl restart cast-viewer.service

set +x

echo "Update completed."
