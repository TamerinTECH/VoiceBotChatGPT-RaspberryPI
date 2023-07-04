#!/bin/bash

# replace this value
SERVICE_NAME="GPTVoiceBot"

# Stop the service
systemctl stop $SERVICE_NAME

# Disable the service
systemctl disable $SERVICE_NAME

# Remove the service file
rm /etc/systemd/system/$SERVICE_NAME.service

# Reload the systemd daemon
systemctl daemon-reload

# Reset the failed state (optional)
systemctl reset-failed

echo "The $SERVICE_NAME has been removed"
