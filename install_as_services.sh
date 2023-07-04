#!/bin/bash

# replace these values
SERVICE_NAME="GPTVoiceBot"
SCRIPT_DIR="/home/pi/VoiceBotChatGPT-RaspberryPI"
SCRIPT_PATH="$SCRIPT_DIR/main.py"
USER_NAME="pi"

echo "[Unit]
Description=VoiceBot Service
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_PATH
User=$USER_NAME
Restart=always

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/$SERVICE_NAME.service

chmod 644 /etc/systemd/system/$SERVICE_NAME.service

# Reload the systemd daemon
systemctl daemon-reload

# Enable the service
systemctl enable $SERVICE_NAME.service

# Start the service
systemctl start $SERVICE_NAME.service

echo "The $SERVICE_NAME has been installed and started"
