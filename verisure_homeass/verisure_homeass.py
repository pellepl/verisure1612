import sys, os
from pocketsphinx import *
import time
import alsaaudio
import numpy as np
import array
import pygame
from pygame.locals import *

modeldir = "/usr/local/share/pocketsphinx/model"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
config.set_string('-dict', './3047.dic')
config.set_string('-lm', './3047.lm')
config.set_string('-logfn', '/dev/null')
config.set_string('-vad_threshold', '5')
config.set_string('-samprate', '16000/8000/48000')

# constants
CHANNELS  = 1
INFORMAT  = alsaaudio.PCM_FORMAT_S16_LE
RATE      = 16000
FRAMESIZE = 2048

# Process audio chunk by chunk.
# On keyword detected perform action and restart search
decoder = Decoder(config)

listen_time = 0

decoder.start_utt()
utt_started = False
in_speech = False

print "Ready..."

# init pygame and audio
pygame.mixer.pre_init(16000, -16, 1, 1024)
pygame.init()
pygame.mixer.init()

# init display
pygame.font.init()
myfont = pygame.font.SysFont("courier new", 24, True)
size = (800,60)
screen = pygame.display.set_mode(size)
time.sleep(1)

setup_mic = True

while True:

    if setup_mic:
        # set up audio input
        recorder=alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
        recorder.setchannels(CHANNELS)
        recorder.setrate(RATE)
        recorder.setformat(INFORMAT)
        recorder.setperiodsize(FRAMESIZE)
        setup_mic = False

    buf = recorder.read()[1]
    len = recorder.read()[0]

    if buf:
        sys.stdout.write('.')
        sys.stdout.flush()

        decoder.process_raw(buf, False, False)

        in_speech = decoder.get_in_speech()
        listen_time = listen_time + 1

        if ((in_speech == True) and (utt_started == False)):
            utt_started = True
            print "Listening..."
            listen_time = 0

        if (((in_speech == False) and (utt_started == True)) or ((utt_started == True) and (listen_time > (2*RATE/FRAMESIZE)))):
            # Speech -> Silence transition, time to start new utterance
            decoder.end_utt()
            print "Analyzing..."

            recorder.pause(True)

            if decoder.hyp() != None:
                hypothesis = decoder.hyp()
                hstr       = hypothesis.hypstr
                logmath    = decoder.get_logmath()
                confidence = logmath.exp(hypothesis.prob)

                print 'Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", confidence

                print 'Detection: Best hypothesis segments:', [seg.word for seg in decoder.seg()]

                rec_message = ""
                do_talk = False
                for seg in decoder.seg():
                    word = seg.word
                    # check for paranthesis
                    parpos = word.find('(')
                    if (parpos > 0):
                        word = word[:parpos]
                    print "word:" + word
                    if word.isalpha():
                        do_talk = True
                        rec_message = rec_message + word.lower() + " "

                # Print recoreded message
                screen.fill((0,0,0))
                mytex = myfont.render(rec_message, False, (0,0,255))
                screen.blit(mytex, (10,10))
                pygame.display.update()

                # Process recorded message
                if do_talk:
                    # Echo back message
                    print "ECHO recorded message:" + rec_message
                    # create wave file with spoken words
                    cmd = "pico2wave -l en-GB -w rec_message.wav \"" + rec_message + "\""
                    print cmd
                    os.system(cmd)
                    # send wave file till speaker
                    pygame.mixer.music.load("rec_message.wav")
                    pygame.mixer.music.play()
                    print "Sound start"
                    while pygame.mixer.music.get_busy():
                        time.sleep(1)
                    print "Sound end"
                    time.sleep(1)
                else:
                    print "No words found in recording."

                # start new utt
                decoder.start_utt()
                utt_started = False
                print "Restarting."

            recorder.pause(False)
            setup_mic = True
            print "Setup mic again..."

        time.sleep(0.1)
