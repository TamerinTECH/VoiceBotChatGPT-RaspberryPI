#!/bin/bash

# replace these values
SERVICE_NAME="GPTVoiceBot"
SCRIPT_DIR="/home/pi/VoiceBotChatGPT-RaspberryPI"
SCRIPT_PATH="$SCRIPT_DIR/main.py"
USER_NAME="pi"

echo "[Unit]
Description=VoiceBot Service
Requires=seeed-voicecard.service
After=network.target multi-user.target

[Service]
StandardOutput=journal
StandardError=journal

Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 $SCRIPT_PATH
User=$USER_NAME
Restart=on-abort

Environment="PULSE_SERVER=/run/user/1000/pulse/native"


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
