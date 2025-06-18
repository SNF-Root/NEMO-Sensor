#!/bin/bash
DEVICE="/dev/ttyUSB0"
FILE=${1:-main.py}

echo "📤 Uploading $FILE to MicroPython..."
mpremote connect $DEVICE fs cp "$FILE" :
