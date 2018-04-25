FROM resin/raspberrypi3-debian:stretch
LABEL authors="Viktor Petersson <vpetersson@screenly.io>,Michel Bardelmeijer <michel@enflow.nl>"

RUN apt-get update && \
    apt-get -y --no-install-recommends install build-essential \
        cron \
        dos2unix \
        git-core \
        net-tools \
        python-netifaces \
        python-simplejson \
        python-dbus \
        python-dev \
        libffi-dev \
        libssl-dev \
        curl \
        psmisc \
        matchbox \
        omxplayer \
        x11-xserver-utils \
        xserver-xorg \
        x11-apps \
        chromium \
        htop \
        cec-utils \
        mediainfo \
        libpng12-dev \
        libraspberrypi-dev \
        imagemagick \
        dnsmasq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# enable container init system.
ENV INITSYSTEM on

# Install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN curl -s https://bootstrap.pypa.io/get-pip.py | /usr/bin/python && \
    /usr/bin/env python -m pip install --upgrade --force-reinstall -r /tmp/requirements.txt

RUN curl https://api.github.com/repos/resin-io/resin-wifi-connect/releases/latest -s \
    | grep -hoP 'browser_download_url": "\K.*rpi\.tar\.gz' \
    | xargs -n1 curl -Ls \
    | tar -xvz -C /usr/local/bin

# Install services
COPY conf/X.service /etc/systemd/system/X.service
COPY conf/matchbox.service /etc/systemd/system/matchbox.service
COPY conf/beamy.service /etc/systemd/system/beamy.service

RUN systemctl enable X.service && \
    systemctl enable matchbox.service && \
    systemctl enable beamy.service

# Install Emoji fonts
COPY conf/50-noto-color-emoji.conf /etc/fonts/conf.d/50-noto-color-emoji.conf
COPY www/fonts/raleway-bold.ttf /usr/share/fonts
COPY www/fonts/raleway-regular.ttf /usr/share/fonts

RUN curl https://raw.githubusercontent.com/googlei18n/noto-emoji/master/fonts/NotoColorEmoji.ttf -o /usr/share/fonts/NotoColorEmoji.ttf && \
    /usr/bin/fc-cache -f -v

# Install config file and file structure
RUN mkdir -p /root/beamy
COPY . /root/beamy

# Install pngview
RUN cd /tmp && \
    git clone https://github.com/AndrewFromMelbourne/raspidmx.git && \
    cd raspidmx/lib && \
    make && \
    cp libraspidmx.so.1 /usr/lib && \
    cd ../pngview && \
    make && \
    cp pngview /usr/bin

# Add additional checkwifi script
COPY bin/checkwifi.sh /usr/local/bin/checkwifi.sh
RUN chmod +x /usr/local/bin/checkwifi.sh && echo "*/5 * * * * /usr/local/bin/checkwifi.sh" | crontab

WORKDIR /root/beamy

RUN dos2unix bin/start.sh

CMD ["bash", "bin/start.sh"]
