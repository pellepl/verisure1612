import sys, os
from pocketsphinx import *
##import pyaudio
import time
import alsaaudio
import numpy as np
import array
#import pygame
#import pyglet

#modeldir = "../../../model"
modeldir = "/usr/local/share/pocketsphinx/model"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', os.path.join(modeldir, 'en-us/en-us'))
#config.set_string('-dict', os.path.join(modeldir, 'en-us/cmudict-en-us.dict'))
config.set_string('-dict', '../4871.dic')
config.set_string('-lm', '../4871.lm')
#config.set_string('-kws', 'keyphrase.list')
config.set_string('-logfn', '/dev/null')

#config.set_string('-nfft', '4096')
#config.set_string('-nfft', '512')
config.set_string('-vad_threshold', '4')
config.set_string('-samprate', '16000/8000/48000')
#config.set_string('-samprate', '16000')
config.set_string('-agc', 'noise')

#config.set_string('-ds2', '')
#config.set_string('-topn2', '')
#config.set_string('-bestpath', '0')
#config.set_string('-maxwpf', '5')
#config.set_string('-kdmaxdepth', '7')
#config.set_string('-kdmaxbbi', '15')
#config.set_string('-pl_window', '10')

#ps = Pocketsphinx(**config)

##XX p = pyaudio.PyAudio()
##XX stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
##XX stream.start_stream()

# constants
CHANNELS = 1
#INFORMAT = alsaaudio.PCM_FORMAT_FLOAT_LE
INFORMAT = alsaaudio.PCM_FORMAT_S16_LE
#RATE = 44100
RATE = 16000
FRAMESIZE = 2048

# set up audio input
recorder=alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
recorder.setchannels(CHANNELS)
recorder.setrate(RATE)
recorder.setformat(INFORMAT)
recorder.setperiodsize(FRAMESIZE)

# Process audio chunk by chunk. On keyword detected perform action and restart search
decoder = Decoder(config)

#pygame.init()

#all = []
listen_time = 0

#decoder.start_utt()

decoder.start_utt()
utt_started = False

in_speech = False

print "Ready..."

while True:

##XX    buf = stream.read(1024)

    buf = recorder.read()[1]
    len = recorder.read()[0]
#    print len
 
#    all.append(buf)
#    time.sleep(1)
#    c = c + 1
#    if c == 20:
#        print "bummer"
##XX        stream.stop_stream()
##XX        stream.close()
##XX        p.terminate()

    if buf:
#        sys.stdout.write('.')
#        sys.stdout.flush()

        decoder.process_raw(buf, False, False)

        in_speech = decoder.get_in_speech()
#        print in_speech
        listen_time = listen_time + 1

        if ((in_speech == True) and (utt_started == False)):
            utt_started = True
            print "Listening..."
            listen_time = 0

        if (((in_speech == False) and (utt_started == True)) or ((utt_started == True) and (listen_time > (2*RATE/FRAMESIZE)))):
            # Speech -> Silence transition, time to start new utterance
            decoder.end_utt()
            print "Analyzing..."
            
            if decoder.hyp() != None:
                hypothesis = decoder.hyp()
                hstr       = hypothesis.hypstr
                logmath    = decoder.get_logmath()
                confidence = logmath.exp(hypothesis.prob)

                print 'Best hypothesis: ', hypothesis.hypstr, " model score: ", hypothesis.best_score, " confidence: ", confidence

                print 'Detection: Best hypothesis segments:', [seg.word for seg in decoder.seg()]

                talky = ""
                do_talk = False
                for seg in decoder.seg():
                    word = seg.word
                    print "word:" + word
                    if word.isalpha():
                        do_talk = True
                        talky = talky + word.lower() + " "

                # Talk
                if do_talk:
                    print talky

                    # XX
                    cmd = "pico2wave -l en-GB -w test.wav \"" + talky + "\""
                    #cmd = "espeak \"" + talky + "\""
                    #cmd = "flite \"" + talky + "\""
                    print cmd
                    os.system(cmd)

                    #pygame.mixer.music.load("test.wav")
                    #pygame.mixer.music.play()
                    #pygame.event.wait()                    
                    #music = pyglet.resource.media('test.wav')
                    #music.play()
                    #pyglet.app.run()
                    #os.system("aplay -N test.wav")
#                    os.system("aplay test.wav")
                    os.system("mplayer test.wav")

                # start new utt
                decoder.start_utt()
                utt_started = False

        time.sleep(0.1)
