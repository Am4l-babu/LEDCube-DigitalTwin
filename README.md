<div align="center">

```
    ██╗     ███████╗██████╗      ██████╗██╗   ██╗██████╗ ███████╗
    ██║     ██╔════╝██╔══██╗    ██╔════╝██║   ██║██╔══██╗██╔════╝
    ██║     █████╗  ██║  ██║    ██║     ██║   ██║██████╔╝█████╗  
    ██║     ██╔══╝  ██║  ██║    ██║     ██║   ██║██╔══██╗██╔══╝  
    ███████╗███████╗██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗
    ╚══════╝╚══════╝╚═════╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
                     D I G I T A L   T W I N
```

# ✨ LEDCube Digital Twin

**A real-time 3D digital twin of a 4×4×4 LED Cube, controlled over WiFi using an ESP8266 and a Python VPython simulation.**

[![PlatformIO](https://img.shields.io/badge/PlatformIO-ESP8266-orange?logo=platformio)](https://platformio.org)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![VPython](https://img.shields.io/badge/VPython-3D%20Simulation-green)](https://vpython.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🌟 What Is This?

This project bridges the physical and digital worlds. Click an LED in a **browser-based 3D simulation**, and the **real LED on the hardware cube lights up** — instantly, over your local WiFi network.

```
[Python Simulation]  ──UDP packet──▶  [ESP8266 NodeMCU]  ──GPIO──▶  [Physical LED]
     VPython 3D                         192.168.x.x:4210              LED Cube Layer
```

It's a **Digital Twin** — the virtual model and the physical hardware stay in perfect sync. Toggle LEDs by clicking in the simulation, and the hardware mirrors every state change in real-time.

---

## 📸 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      DIGITAL TWIN SYSTEM                        │
│                                                                  │
│  ┌──────────────┐    WiFi (UDP)    ┌──────────────────────┐     │
│  │  PC / Laptop │ ──────────────▶  │  ESP8266 NodeMCU     │     │
│  │              │                  │                      │     │
│  │  simulation  │  192.168.x.x     │  GPIO 0,2,4,5,12,   │     │
│  │  .py         │  Port: 4210      │  13,14,15,16         │     │
│  │  (VPython)   │ ◀──────────────  │                      │     │
│  └──────────────┘    Status/ACK    └──────────┬───────────┘     │
│                                               │                  │
│                                    ┌──────────▼───────────┐     │
│                                    │   Physical LED Cube  │     │
│                                    │   (4×4×4 = 64 LEDs)  │     │
│                                    └──────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Hardware Requirements

| Component | Details |
|---|---|
| **Microcontroller** | ESP8266 NodeMCU v2 (ESP-12E) |
| **LEDs** | 9 (expandable to 64 with shift registers) |
| **Communication** | WiFi 802.11 b/g/n |
| **Power** | USB 5V via NodeMCU USB port |
| **Connection** | USB-Serial CH340 (or CP2102) |

### 📌 ESP8266 GPIO Pin Mapping

```
NodeMCU Pin │ GPIO │ LED Index
────────────┼──────┼───────────
    D0      │  16  │   LED 0
    D1      │   5  │   LED 1
    D2      │   4  │   LED 2
    D3      │   0  │   LED 3
    D4      │   2  │   LED 4
    D5      │  14  │   LED 5
    D6      │  12  │   LED 6
    D7      │  13  │   LED 7
    D8      │  15  │   LED 8
```

> **Note:** The ESP8266 has 9 usable digital GPIOs. To drive a full 4×4×4 (64-LED) cube, use shift registers (e.g., 74HC595) to expand outputs.

---

## 💻 Software Requirements

### Firmware (ESP8266)
- [PlatformIO](https://platformio.org/) IDE or CLI
- `espressif8266` platform (auto-installed by PlatformIO)
- Arduino framework

### Simulation (PC)
- Python 3.8+
- `vpython` — 3D browser-based rendering
- `python-dotenv` — environment variable management

Install Python dependencies:
```bash
pip install vpython python-dotenv
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Am4l-babu/LEDCube-DigitalTwin.git
cd LEDCube-DigitalTwin
```

### 2. Configure WiFi Credentials

Copy the secrets template and fill in your network details:

```bash
cp src/arduino_secrets_template.h src/arduino_secrets.h
```

Edit `src/arduino_secrets.h`:

```cpp
#define SECRET_SSID "YourWiFiSSID"
#define SECRET_PASS "YourWiFiPassword"
#define SECRET_PC_IP "192.168.x.x"   // IP of the machine running simulation.py
```

> ⚠️ `arduino_secrets.h` is git-ignored. **Never commit real credentials.**

### 3. Flash the ESP8266

Ensure the NodeMCU is connected via USB, then:

```bash
pio run --target upload
```

Open the serial monitor to find the ESP's IP address:

```bash
pio device monitor --baud 115200
```

Look for output like:
```
WiFi Connected!
ESP IP Address: 192.168.1.6
UDP Listening on port 4210
```

### 4. Configure the Simulation

Copy the environment template:

```bash
cp .env.template .env
```

Edit `.env` with the IP address from the serial monitor:

```env
ESP_IP=192.168.1.6
UDP_PORT=4210
```

### 5. Run the Digital Twin Simulation

```bash
python simulation.py
```

A browser tab will open at `http://localhost:8000` showing the interactive 3D LED cube.

---

## 🎮 How to Use the Simulation

| Action | Result |
|---|---|
| **Click an LED** | Toggles it ON/OFF (syncs to physical hardware) |
| **Click "Clear All"** | Turns off all LEDs in simulation and hardware |
| **Drag to rotate** | Orbit the 3D cube view |
| **Scroll wheel** | Zoom in / out |
| **Hover over LED** | LED highlights to confirm selection |

### LED Layer Color Coding

```
Layer 0 (Bottom) │ 🔵 Blue
Layer 1          │ 🟡 Yellow
Layer 2          │ 🟢 Green
Layer 3 (Top)    │ 🔴 Red
```

---

## 📡 UDP Communication Protocol

Commands are sent as 4-byte UDP packets:

```
Byte 0: Command type → 'C' (0x43) — Set LED state
Byte 1: Layer index  → 0–3
Byte 2: LED index    → 0–8 (or 0–15 for full 4×4 layer)
Byte 3: State        → 1 = ON, 0 = OFF
```

Example — Turn on LED 3 in Layer 0:
```python
import socket, struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
packet = struct.pack('BBBB', ord('C'), 0, 3, 1)
sock.sendto(packet, ('192.168.1.6', 4210))
```

---

## 📁 Project Structure

```
LEDCube-DigitalTwin/
│
├── src/
│   ├── main.cpp                    # ESP8266 firmware (WiFi + UDP + GPIO)
│   ├── arduino_secrets_template.h  # WiFi credentials template
│   └── arduino_secrets.h           # ← Create this (git-ignored)
│
├── simulation.py                   # Python 3D digital twin simulation
├── platformio.ini                  # PlatformIO build config (ESP8266 NodeMCU)
├── .env.template                   # Environment variable template
├── .env                            # ← Create this (git-ignored)
│
├── include/                        # PlatformIO include directory
├── lib/                            # PlatformIO library directory
└── test/                           # PlatformIO test directory
```

---

## ⚙️ platformio.ini Reference

```ini
[env:nodemcuv2]
platform = espressif8266
board = nodemcuv2
framework = arduino
upload_port = COM6          ; Change to your COM port (Linux: /dev/ttyUSB0)
monitor_port = COM6
monitor_speed = 115200
```

> On Linux/macOS, replace `COM6` with `/dev/ttyUSB0` or `/dev/cu.usbserial-*`.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `This chip is ESP8266, not ESP32` | Ensure `platformio.ini` uses `platform = espressif8266` and `board = nodemcuv2` |
| ESP won't connect to WiFi | Double-check SSID/password in `arduino_secrets.h`, then reflash |
| Simulation opens but LEDs don't light on hardware | Verify `ESP_IP` in `.env` matches the IP in serial monitor |
| `ModuleNotFoundError: vpython` | Run `pip install vpython python-dotenv` |
| Serial garbage on monitor | Confirm baud rate is `115200` in `pio device monitor --baud 115200` |
| COM port not found | Check Device Manager (Windows) or `ls /dev/tty*` (Linux) |

---

## 🗺️ Roadmap

- [x] Single-layer (Layer 0) LED control via UDP
- [x] Interactive 3D VPython simulation with hover effects
- [x] Real-time hardware sync over WiFi
- [ ] Full 4-layer support (64 LEDs with shift registers)
- [ ] Animation sequences (rain, spiral, wave)
- [ ] Web dashboard UI (HTML/JS) as simulation alternative
- [ ] OTA (Over-The-Air) firmware updates
- [ ] MQTT support for IoT platform integration

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

<div align="center">

**Built with ❤️ by [Am4l-babu](https://github.com/Am4l-babu)**

*Where physical hardware meets digital simulation.*

</div>
