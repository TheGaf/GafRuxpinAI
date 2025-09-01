# Teddy Ruxpin Bluetooth Animatronic Controller

A **minimal, robust, and privacy-focused setup**: Your phone does the AI (ChatGPT Voice, Spotify, etc.), and your Raspberry Pi Zero 2 W acts as a Bluetooth speaker with animatronic lipsync—Teddy's mouth and eyes move in real time to audio from your phone.  
**No microphone, no cloud, no APIs, no OpenAI/Spotify keys needed on the Pi.**

---

## Table of Contents

- [Project Overview](#project-overview)
- [Hardware Requirements](#hardware-requirements)
- [Wiring Diagram and Pinout](#wiring-diagram-and-pinout)
- [Setup & Installation](#setup--installation)
- [Bluetooth Pairing & Audio Routing](#bluetooth-pairing--audio-routing)
- [Running the Lipsync Controller](#running-the-lipsync-controller)
- [How It Works](#how-it-works)
- [Configuration & Tuning](#configuration--tuning)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Credits & License](#credits--license)

---

## Project Overview

This project transforms your Raspberry Pi Zero 2 W into a Bluetooth animatronic mouth and eye controller for a Teddy Ruxpin or similar toy.  
**All intelligence, voice, and music come from your phone**—the Pi simply plays the audio and moves the animatronics in sync.

**Features:**
- Acts as a Bluetooth A2DP speaker for your phone (OpenAI Voice, Spotify, Apple Music, YouTube, etc.)
- Animates Teddy’s mouth (DC motor) to real-time audio energy (RMS envelope)
- Animates Teddy’s eyes to blink on a timer
- Minimal dependencies: Python, numpy, sounddevice, RPi.GPIO
- No cloud calls, no privacy risk, no mic or API keys needed

---

## Hardware Requirements

- **Raspberry Pi Zero 2 W** (other Pi models may work)
- **DRV8833 motor driver**
- **2x DC motors** (one for mouth, one for eyes—already inside many Teddy Ruxpins)
- **USB audio dongle** (for reliable sound output)
- **Powered speaker** (3.5mm AUX in, plugs into dongle)
- **Dupont jumper wires** (female-female or as needed)
- **5V power supply** (with 1A inline fuse recommended)
- **Your phone** (iOS/Android, with any TTS/music app)

---

## Wiring Diagram and Pinout

**DRV8833 Connections (BCM GPIO numbering):**

| Function      | DRV8833 Pin | Pi GPIO Pin |
|---------------|-------------|-------------|
| Mouth PWM     | IN1         | GPIO18      |
| Mouth DIR     | IN2         | GPIO23      |
| Eyes Motor A  | IN3         | GPIO24      |
| Eyes Motor B  | IN4         | GPIO25      |
| VCC           | VCC         | Pi 5V       |
| GND           | GND         | Pi GND      |

**Outputs:**
- OUT1/OUT2 → Mouth motor wires inside Teddy
- OUT3/OUT4 → Eyes motor wires inside Teddy

**Other:**
- nSLEEP/EN: Jumper high (to VCC)
- Use a common ground for Pi, DRV8833, speaker, and Teddy

---

## Setup & Installation

1. **Flash Raspberry Pi OS (Bookworm or later) to SD card**
2. **Boot Pi, connect to network, open terminal**
3. **Plug in USB audio dongle and powered speaker**
4. **Connect DRV8833 and motors as per pinout above**

5. **Copy the three project files to your Pi:**
    - `install_bt_audio.sh`
    - `bt_lipsync_min.py`
    - `README.md` (this file)

6. **Run the setup script:**
   ```bash
   chmod +x install_bt_audio.sh
   ./install_bt_audio.sh
   ```
   - Installs all dependencies (Bluetooth, PipeWire/PulseAudio, Python libs)
   - Starts Bluetooth service
   - Guides you through pairing and audio sink setup

---

## Bluetooth Pairing & Audio Routing

1. **Make Pi discoverable and pairable:**
   - Run `bluetoothctl`
   - Type:
     ```
     power on
     agent on
     default-agent
     discoverable on
     pairable on
     ```
2. **On your phone:**  
   - Scan for Bluetooth devices, pair with `raspberrypi`
   - In `bluetoothctl`:  
     ```
     trust <your-phone-MAC>
     pair <your-phone-MAC>
     connect <your-phone-MAC>
     ```
3. **Set the USB audio dongle as the default output:**
   - Run:
     ```bash
     pactl list short sinks
     ```
   - Find the line with `alsa_output.usb-...-analog-stereo`
   - Set as default:
     ```bash
     pactl set-default-sink <that_name>
     ```

---

## Running the Lipsync Controller

1. **Start the lipsync script:**
   ```bash
   python3 bt_lipsync_min.py
   ```
2. **Play audio on your phone** (ChatGPT Voice, Spotify, Apple Music, etc.)
   - Select the Pi as your phone’s Bluetooth audio output
   - Teddy’s mouth and eyes will animate to the sound!

**To stop:**  
- Press Ctrl+C. Script exits and releases motors/GPIO.

---

## How It Works

- **Audio Path:**  
  Phone audio → Bluetooth (A2DP) → Pi → USB audio dongle → Speaker
- **Mouth Animation:**  
  The script measures the real-time RMS energy of the played audio and uses it to control the mouth motor via PWM (mouth opens wider on louder sounds).
- **Eyes Animation:**  
  Eyes motor “blinks” every few seconds (timed pulse).
- **No mic:**  
  The script reads the monitor of the default audio sink (USB dongle), so it “hears” exactly what’s played.

---

## Configuration & Tuning

**Top of `bt_lipsync_min.py`:**

- `MOUTH_PWM`, `MOUTH_DIR`, `EYES_A`, `EYES_B`: GPIO pin numbers (BCM)
- `THRESH`: Mouth open threshold (lower for more movement)
- `GAIN`: RMS gain (higher for softer audio, lower for loud)
- `LAT_MS`: Latency compensation (Bluetooth delay; set >0 ms only if you want added visual delay)
- `BLINK_S`: Eyes blink every X seconds
- `BLINK_MS`: Blink duration in ms

**To customize:**  
Edit these constants and rerun the script.

---

## Troubleshooting

| Symptom                              | Solution |
|---------------------------------------|----------|
| Audio plays, but no mouth/eyes move   | Check wiring, pin numbers, and ground. Confirm DRV8833 power. |
| "No monitor source" error             | Play audio, ensure USB dongle is default output. Run `pactl set-default-sink ...` |
| Motors move backwards                 | Swap output wires or invert DIR logic in script. |
| Bluetooth won’t connect               | Use `bluetoothctl` to re-pair/trust/connect. |
| Script crashes, permission error      | Try `sudo python3 bt_lipsync_min.py` |
| Mouth/eyes stay on after exit         | Ensure script exited cleanly; unplug/repower if needed. |
| "ALSA/pulse device not found"         | Confirm USB dongle detected; try rebooting Pi. |

---

## FAQ

**Q: Does this need a microphone or cloud connection?**  
A: No. All sound and “intelligence” come from your phone.

**Q: Can I use any phone/app?**  
A: Yes! Any app that outputs sound over Bluetooth will work—OpenAI Voice, Spotify, Apple Music, YouTube, etc.

**Q: Is my privacy protected?**  
A: Absolutely. The Pi never records, transcribes, or sends audio anywhere.

**Q: Does it work without a USB audio dongle?**  
A: It’s strongly recommended—onboard Pi audio is unreliable for A2DP.

**Q: Can I run this at boot?**  
A: Yes! You can create a `systemd` service if you want it to auto-start (see below).

---

## Credits & License

Inspired by the magic of Teddy Ruxpin and the maker community.  
Hardware and code:  
- [DRV8833 datasheet](https://www.ti.com/lit/ds/symlink/drv8833.pdf)
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- [sounddevice](https://python-sounddevice.readthedocs.io/)
- [numpy](https://numpy.org/)

MIT License. See `LICENSE` file if present.

---

**Enjoy your magical, AI-powered Teddy Ruxpin—now simpler, safer, and more fun!**
