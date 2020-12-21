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

