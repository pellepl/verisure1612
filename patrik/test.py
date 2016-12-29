#!/usr/bin/env python

from pocketsphinx import LiveSpeech
import pyaudio

#for phrase in LiveSpeech(audio_device='plughw:1,0'): print(phrase)

audio = pyaudio.PyAudio()

try:
    pass;    
finally:
    audio.terminate()
