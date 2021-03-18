#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "[Unit]
Description=Button light
After=network-online.target

[Service]
ExecStart=/bin/bash $DIR/button_run.sh
WorkingDirectory=$DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target" > /lib/systemd/system/ButtonLight.service 

sudo systemctl enable ButtonLight.service
sudo systemctl start ButtonLight.service

#sudo apt-get install lirc
# Add to /boot/config.txt:
#dtoverlay=gpio-ir-tx,gpio_pin=17
#dtoverlay=gpio-ir,gpio_pin=18
# Change /etc/lirc/lirc_options.conf:
# driver=default
# Copy *.conf to /etc/lirc/lircd.conf.d/


