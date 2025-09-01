#!/bin/bash
# Minimal install for Pi Zero 2 W as Bluetooth A2DP speaker with animatronics

set -e

echo "Updating and installing dependencies..."
sudo apt update
sudo apt install -y bluez pulseaudio pulseaudio-module-bluetooth python3-pip python3-numpy python3-sounddevice python3-rpi.gpio mpg123

echo "Enabling and starting bluetooth..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

echo "Add pi user to bluetooth group..."
sudo usermod -aG bluetooth pi

echo "Pair your phone with the Pi:"
echo ""
echo "1. Run: bluetoothctl"
echo "   (then enter: power on, agent on, default-agent, discoverable on, pairable on)"
echo "2. On your phone, pair to 'raspberrypi'."
echo "3. In bluetoothctl: trust <MAC>, pair <MAC>, connect <MAC>"
echo ""
echo "Set the USB audio dongle as default sink:"
echo "  pactl list short sinks"
echo "Find 'alsa_output.usb-...-analog-stereo', then run:"
echo "  pactl set-default-sink <that_name>"
echo ""
echo "Done! Now run: python3 bt_lipsync_min.py"