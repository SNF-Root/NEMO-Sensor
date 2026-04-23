# NEMO-Sensor

> Battery-powered environmental sensors (temperature & humidity) that report into a lab management platform via a local collector server.

---
# Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Hardware](#hardware)
- [Enclosure](#enclosure)
- [Wiring](#wiring)
- [Firmware Setup](#firmware-setup)
- [Collector Setup](#collector-setup)
- [Repository Structure](#repository-structure)
- [Known Issues](#known-issues)

---

## Overview

Commercial environmental sensors are expensive (~$50–80/unit) and typically rely on proprietary cloud ecosystems that can't integrate with custom platforms. This project builds a low-cost alternative at **$10–14 per node** using a **Seeed XIAO ESP32-C3** and a **GY-SHT31-D** temperature & humidity sensor, housed in a custom 3D-printed enclosure with USB-C charging.

Each node wakes on a configurable interval, reads the sensor, POSTs the data to a local collector server over Wi-Fi, and goes back to deep sleep. The collector forwards the data to whatever platform or API you're using. The architecture is intentionally simple and easy to adapt.

---

## System Architecture

```
ESP32 (SHT31) ──Wi-Fi──► Collector Server ──HTTPS──► Your Data Platform
     ×N             Local network only        outbound
```

- **ESP32 nodes** read the sensor and POST JSON to the collector over the local network
- **Collector** runs a Flask server that receives, buffers, and forwards data to your platform
- **Nodes never hold platform credentials** — only the collector does
- Designed for environments where sensor nodes shouldn't have direct internet access

The collector acts as a secure gateway. Swap out `push-to-nemo.py` for whatever API your platform exposes.

---

## Hardware

| Component | Details |
|-----------|---------|
| Microcontroller | Seeed XIAO ESP32-C3 |
| Sensor | GY-SHT31-D Temperature & Humidity (I2C) |
| PCB | Perfboard, 4×6 cm |
| Battery | 2× 3.7V / 3500mAh lithium rechargeable (permanent, charged via USB-C) |
| Enclosure | Custom 3D-printed, 2-piece shell |
| Wires | 4 connections (VIN, GND, SDA, SCL) |

**Cost per node: ~$10–14**

---

## Enclosure

2-piece 3D-printed shell. Designed for easy assembly; open it if you need to, but you shouldn't need to for normal operation.

**Features:**
- 3-walled internal cradle holds the ESP32-C3 in place without adhesive
- USB-C tunnel cutout — charge in-place, no disassembly needed
- Ventilation openings for the SHT31 sensor
- Filleted corners, 2mm minimum wall thickness

**STL files:** `stl/enclosure_bottom.stl`, `stl/enclosure_top.stl`

**Print settings:**

| Parameter | Value |
|-----------|-------|
| Material | PLA |
| Layer height | 0.2 mm (or lower for detail areas) |
| Infill | 15% |
| Wall count | 3 perimeters |
| Wall speed | 60 mm/s (outer wall), 20 mm/s (inner wall) |

---

## Wiring

Both boards are soldered onto a 4×6 cm perfboard.

| SHT31 Pin | ESP32-C3 Pin | Wire Color |
|-----------|-------------|------------|
| VIN | 3V3 | Red |
| GND | GND | Black |
| SDA | GPIO6 | Teal/Purple |
| SCL | GPIO7 | Yellow |

> I2C at 3.3V logic. Default SHT31 address: `0x44` (fallback: `0x45`)

Battery wired directly to BAT+ / BAT− pads on the back of the ESP32-C3. No external voltage regulator needed — the onboard charger handles that.

---

## Firmware Setup

### Requirements

- Python 3 with `esptool` and `mpremote` installed
- MicroPython firmware: `ESP32_GENERIC_C3-20251209-v1.27.0.bin`
  - Download: [micropython.org/download/ESP32_GENERIC_C3](https://micropython.org/download/ESP32_GENERIC_C3/)

### Files to Upload

| File | Purpose |
|------|---------|
| `esp32/main.py` | Main firmware loop |
| `esp32/sht31.py` | SHT31 sensor driver |
| `esp32/read_env.py` | Config file parser |
| `config.env` | Your credentials — **not in repo, create locally** |

### config.env Format

```
SSID=your_wifi_name
PASSWORD=your_wifi_password
API_URL=http://your-collector-ip:port/submit
AUTH_TOKEN=your_platform_token
SHT31_TEMP_ID=123
SHT31_HUMD_ID=124
SLEEP_TIME_IN_MS=900000
```

> `config.env` is in `.gitignore` — never commit it.

---

### ⚠️ Important: Uploading Code to a Sleeping Board

Once `main.py` is on the device, the board will immediately run it on every boot — which means it will read the sensor, post data, and enter deep sleep within seconds. **Do not try to race the board to upload new code before it sleeps.**

If you need to upload updated code to a board that already has `main.py` on it, the correct approach is:

1. Put the board into **bootloader mode** (hold the BOOT button, press and release RESET, then release BOOT)
2. Erase the flash completely
3. Re-flash MicroPython
4. Upload all files fresh

This is the same process as a first-time flash — see the steps below.

---

### Flash & Upload (Linux)

Use the provided script:

```bash
cd esp32/
chmod +x flash_and_upload.sh
./flash_and_upload.sh
```

Or step by step:

```bash
# 1. Erase flash
esptool.py --port /dev/ttyUSB0 erase_flash

# 2. Flash MicroPython
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 \
  write_flash -z 0x0 ESP32_GENERIC_C3-20251209-v1.27.0.bin

# 3. Upload files
mpremote connect /dev/ttyUSB0 cp main.py :main.py
mpremote connect /dev/ttyUSB0 cp sht31.py :sht31.py
mpremote connect /dev/ttyUSB0 cp read_env.py :read_env.py
mpremote connect /dev/ttyUSB0 cp config.env :config.env

# 4. Soft reset
mpremote connect /dev/ttyUSB0 repl  # then Ctrl+D
```

### How It Works

Each wake cycle:

1. Soft-reset the SHT31
2. Read temp & humidity over I2C (50kHz first read → 100kHz after, to avoid RF glitches)
3. Connect to Wi-Fi
4. POST two JSON payloads to the collector — one for temperature, one for humidity
5. Disconnect, `gc.collect()`, deep sleep for `SLEEP_TIME_IN_MS`

---

## Collector Setup

The collector is a small Python server that sits on your local network, receives data from the ESP32 nodes, and forwards it to your data platform.

### Files

| File | Purpose |
|------|---------|
| `collector/receive-logic.py` | Flask server — receives JSON from nodes, buffers to `sensor_data.json` |
| `collector/push-to-nemo.py` | Reads the buffer, pushes to your platform's API every 60s |
| `collector/collector.py` | Combined version — alternate deployment option |

### Adapting to Your Platform

The push script (`push-to-nemo.py`) is the only platform-specific piece. It reads from the local JSON buffer and POSTs to an API endpoint with an auth token. Replace the endpoint and auth logic to match whatever platform you're integrating with.

Each payload looks like:

```json
{
  "sensor": 42,
  "value": 21.34,
  "created_date": "2025-03-15T14:22:01Z"
}
```

Two payloads per cycle — one for temperature, one for humidity. Each maps to a separate sensor ID on your platform.

---

## Repository Structure

```
NEMO-Sensor/
├── esp32/
│   ├── main.py               # Main firmware (XIAO ESP32-C3 v2.0)
│   ├── sht31.py              # SHT31 driver
│   ├── read_env.py           # Config loader
│   ├── flash_and_upload.sh   # Flash firmware + upload all files
│   ├── upload.sh             # Upload files only (no flash)
│   ├── mprun                 # mpremote helper script
│   ├── mq135.py              # Gas sensor driver (future, not active)
│   └── w104.py               # Battery voltage monitor (future, not active)
├── collector/
│   ├── collector.py          # Flask receiver + platform forwarder
│   ├── receive-logic.py      # Data ingestion logic
│   └── push-to-nemo.py       # Platform push script (adapt to your API)
├── raspberrypi/              # Early Raspberry Pi prototype
│   ├── sensor_module.py
│   └── sensor-collect-send.py
├── stl/                      # 3D print files (enclosure)
├── .gitignore
└── README.md
```

---

## Known Issues

| Item | Notes |
|------|-------|
| Weak Wi-Fi range | The XIAO ESP32-C3's built-in antenna is small and has limited range. External antennas compatible with the board are available separately and are the recommended fix for range-limited deployments. |
| Battery percentage monitoring | The ESP32-C3 has no ADC pin, so battery voltage cannot be read without an additional component. No workaround is currently implemented. |
| BAT pad fragility | The battery solder pads on the back of the XIAO ESP32-C3 are fragile and can detach if the board is handled roughly or removed from the enclosure repeatedly. A detached pad makes the board unusable for battery-powered operation. Keep the board in the enclosure and avoid unnecessary removal. |

---

*Built at the Stanford Nanofabrication Facility.*
