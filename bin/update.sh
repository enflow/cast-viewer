#!/bin/bash -e

set -x
set -e

cd /home/pi/cast-viewer

git fetch --tags
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
CURRENT_TAG=$(git rev-parse --abbrev-ref HEAD)

if [ "$LATEST_TAG" -eq "$CURRENT_TAG" ]
then
    echo "No new update."
    exit 0
fi

git checkout ${LATEST_TAG}

cd /home/pi/cast-viewer/ansible
ansible-playbook site.yml

set +x
set +e
echo "Update completed."
