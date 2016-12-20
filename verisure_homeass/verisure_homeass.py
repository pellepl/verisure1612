import sys, os
from pocketsphinx import *
import time
import alsaaudio
import numpy as np
import array
import pygame
from pygame.locals import *
import PyInterpreter

modeldir = "/usr/local/share/pocketsphinx/model"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
config.set_string('-dict', './0585.dic')
config.set_string('-lm', './0585.lm')
config.set_string('-logfn', '/dev/null')
config.set_string('-vad_threshold', '4')
config.set_string('-samprate', '16000/8000/48000')
config.set_string('-agc', 'max')

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
myfont = pygame.font.SysFont("courier new", 32, True)
size = (800,240)
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
        recimg = pygame.image.load("microphone.png")
        recimg = pygame.transform.scale(recimg, (150,150))
        screen.fill((0,0,0))
        screen.blit(recimg, (350,50))
        pygame.display.update()

    buf = recorder.read()[1]
    len = recorder.read()[0]

    if buf:
#        sys.stdout.write('.')
#        sys.stdout.flush()

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
            # Notify user analyzing state
            screen.fill((0,0,0))
            mytex = myfont.render("...analyzing input...", False, (100,100,255))
            screen.blit(mytex, (50,50))
            pygame.display.update()

            recorder.pause(True)

            if decoder.hyp() != None:
                hypothesis = decoder.hyp()
                hstr       = hypothesis.hypstr
                logmath    = decoder.get_logmath()
                confidence = logmath.exp(hypothesis.prob)

                print 'Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", confidence

                print 'Detection: Best hypothesis segments:', [seg.word for seg in decoder.seg()]

                rec_message = ""
                found_words = 0
                for seg in decoder.seg():
                    word = seg.word.lower()
                    # check for paranthesis
                    parpos = word.find('(')
                    if (parpos > 0):
                        word = word[:parpos]
                    # check for Verisure alternatives
                    if (word.startswith('ver')):
                        word = 'verisure'
                    #print "word:" + word
                    if word.isalpha():
                        found_words = found_words + 1
                        rec_message = rec_message + word + " "

                # Print recoreded message
                screen.fill((0,0,0))
                mytex = myfont.render("input: " + rec_message, False, (200,200,255))
                screen.blit(mytex, (10,10))
                pygame.display.update()

                # Process recorded message
                if found_words > 1:

                    # Interpret
                    print "INTERPRET: " + rec_message
                    interp_command = PyInterpreter.interpret( rec_message )
                    if interp_command == None:
                        interp_command = "Sorry I did not understand "
                        rec_message = "Sorry I did not understand " + rec_message
                    print "COMMAND: " + interp_command

                    # Print feedback
                    mytex = myfont.render("output: " + interp_command, False, (200,200,255))
                    screen.blit(mytex, (10,200))
                    pygame.display.update()

                    # Echo back message
                    print "ECHO recorded message: " + rec_message
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
