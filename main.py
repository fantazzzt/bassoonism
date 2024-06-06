import pyaudio
import sys
import numpy as np
from pynput.keyboard import Controller, Key
import time
import mappings
import configs
from aubio import sink
import datetime

DEBUG = False

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

if DEBUG:
    now = datetime.datetime.now()
    audio_sink = sink(str(now), samplerate)
else:
    audio_sink = None

# Setup pitch detection
pitch_o = configs.create_pitch_detector()

keyboard = Controller()

def play_key(note):
    key = mappings.note_to_key.get(note, None)
    if key:
        keyboard.press(key)
        time.sleep(0.1)
        keyboard.release(key)

print("*** recording")
while True:
    try:
        audiobuffer = stream.read(buffer_size)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()

        if confidence > 0.8:
            midi_note = int(round(pitch))
            print(f"Detected note: {midi_note}")
            play_key(midi_note) # ONLY APPLIES TO ACTIVE WINDOW

        if audio_sink:
            audio_sink(signal, len(signal))

    except KeyboardInterrupt:
        print("*** Ctrl+C pressed, exiting")
        break

print("*** stopped recording")
stream.stop_stream()
stream.close()
p.terminate()
