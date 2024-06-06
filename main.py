import pyaudio
import sys
import numpy as np
import aubio
from pynput.keyboard import Controller, Key
import time
import mappings

# Initialise pyaudio
p = pyaudio.PyAudio()

# Open stream
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

# Record duration 
if len(sys.argv) > 1:
    record_duration = 5 
    total_frames = 0
else:
    record_duration = None

# Setup pitch detection
tolerance = 0.8
win_s = 4096  # FFT size
hop_s = buffer_size  # Hop size
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

# Keyboard controller
keyboard = Controller()

def play_key(note):
    key = mappings.note_to_key.get(note, None)
    if key:
        keyboard.press(key)
        time.sleep(0.1)
        keyboard.release(key)

print("*** starting recording")
while True:
    try:
        audiobuffer = stream.read(buffer_size)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()

        if confidence > 0.8:  # Only consider notes with high confidence
            midi_note = int(round(pitch))
            print(f"Detected note: {midi_note}")
            play_key(midi_note)

        if record_duration:
            total_frames += len(signal)
            if record_duration * samplerate < total_frames:
                break
    except KeyboardInterrupt:
        print("*** Ctrl+C pressed, exiting")
        break

print("*** done recording")
stream.stop_stream()
stream.close()
p.terminate()
