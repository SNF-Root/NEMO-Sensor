#!/bin/bash

# === CONFIGURATION ===
PORT="/dev/ttyUSB0"
BAUD=460800
FIRMWARE="ESP32_GENERIC-20250415-v1.25.0.bin"  # Change to your firmware file
FILES=("main.py" "sht31.py" "mq135.py" "read_env.py" "w104.py")  # Add all necessary scripts

# === FLASH FIRMWARE ===
echo "🔄 Erasing flash..."
esptool.py --port "$PORT" erase_flash

echo "⚡ Flashing firmware..."
esptool.py --chip esp32 --port "$PORT" --baud "$BAUD" write_flash -z 0x1000 "$FIRMWARE"

# Wait a few seconds for reboot
echo "⏳ Waiting for device to reboot..."
sleep 5

# === UPLOAD FILES ===
for file in "${FILES[@]}"; do
    echo "📤 Uploading $file..."
    mpremote connect "$PORT" fs cp "$file" :
done

# === OPTIONAL: Run main.py ===
echo "🚀 Running main.py..."
mpremote connect "$PORT" run main.py

echo "✅ Done!"
