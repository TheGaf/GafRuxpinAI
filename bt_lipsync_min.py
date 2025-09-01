#!/usr/bin/env python3
"""
Minimal Teddy Ruxpin animatronic controller.
- Receives Bluetooth (A2DP) audio (from phone) via Pi (PulseAudio/PipeWire)
- Plays audio out USB dongle
- Animates mouth (PWM) to audio envelope
- Blinks eyes every few seconds
No mic, no cloud, no APIs.
"""

import time
import numpy as np
import sounddevice as sd
import RPi.GPIO as GPIO

# --- Pin definitions (BCM) ---
MOUTH_PWM = 18  # PWM for mouth (DRV8833 IN1)
MOUTH_DIR = 23  # DIR for mouth (DRV8833 IN2)
EYES_A    = 24  # Eyes motor A (DRV8833 IN3)
EYES_B    = 25  # Eyes motor B (DRV8833 IN4)

THRESH = 0.015     # RMS open threshold
GAIN = 40.0        # RMS gain (tune for your system)
LAT_MS = 160       # Bluetooth latency compensation (ms)
BLINK_S = 4.0      # Eyes blink period (seconds)
BLINK_MS = 120     # Eyes blink duration (ms)

AUDIO_BLOCK_MS = 30
AUDIO_FS = 16000   # Reasonably low for RMS envelope

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOUTH_PWM, GPIO.OUT)
    GPIO.setup(MOUTH_DIR, GPIO.OUT)
    GPIO.setup(EYES_A, GPIO.OUT)
    GPIO.setup(EYES_B, GPIO.OUT)
    # Set up PWM for mouth
    pwm = GPIO.PWM(MOUTH_PWM, 1000)
    pwm.start(0)
    return pwm

def cleanup(pwm):
    pwm.ChangeDutyCycle(0)
    GPIO.output(MOUTH_DIR, GPIO.LOW)
    GPIO.output(EYES_A, GPIO.LOW)
    GPIO.output(EYES_B, GPIO.LOW)
    GPIO.cleanup()

def blink_eyes():
    GPIO.output(EYES_A, GPIO.HIGH)
    GPIO.output(EYES_B, GPIO.LOW)
    time.sleep(BLINK_MS / 1000.0)
    GPIO.output(EYES_A, GPIO.LOW)
    GPIO.output(EYES_B, GPIO.LOW)

def main():
    print("=== Teddy Bluetooth Lipsync (minimal, no mic) ===")
    print("Make sure your phone is paired and playing to the Pi (USB speaker plugged in).")
    print("If you see a 'no monitor source' error, set the USB dongle as default sink (see README).")
    pwm = setup_gpio()
    block_samples = int(AUDIO_FS * AUDIO_BLOCK_MS / 1000)
    last_blink = time.time()
    mouth_open = False

    # Find the first PulseAudio/PipeWire monitor device
    devices = sd.query_devices()
    monitor_idx = None
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0 and ('monitor' in d['name'].lower()):
            monitor_idx = i
            break
    if monitor_idx is None:
        print("ERROR: No PulseAudio/PipeWire monitor found.")
        print("Pair phone, play audio, and set USB sink default via pactl.")
        exit(1)
    print(f"Using monitor device: {devices[monitor_idx]['name']}")

    try:
        with sd.InputStream(device=monitor_idx, channels=1, samplerate=AUDIO_FS, blocksize=block_samples) as stream:
            print("Ready! Teddy will lipsync to any audio from your phone...")
            while True:
                audio, _ = stream.read(block_samples)
                audio = np.squeeze(audio)
                rms = np.sqrt(np.mean((audio * GAIN) ** 2))
                # Simple envelope smoothing
                mouth_val = np.clip((rms - THRESH) / (1.0 - THRESH), 0, 1)
                duty = int(100 * mouth_val)
                if mouth_val > 0.05:
                    GPIO.output(MOUTH_DIR, GPIO.HIGH)
                    pwm.ChangeDutyCycle(duty)
                    mouth_open = True
                else:
                    GPIO.output(MOUTH_DIR, GPIO.LOW)
                    pwm.ChangeDutyCycle(0)
                    mouth_open = False

                now = time.time()
                if now - last_blink > BLINK_S:
                    blink_eyes()
                    last_blink = now

                # Latency compensation (optional)
                time.sleep(max(0, AUDIO_BLOCK_MS/1000.0 - (LAT_MS/1000.0 if mouth_open else 0)))
    except KeyboardInterrupt:
        print("\nExiting, cleaning up...")
    finally:
        cleanup(pwm)
        print("Bye!")

if __name__ == "__main__":
    main()