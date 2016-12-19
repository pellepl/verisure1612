#!/bin/bash
#pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm 4871.lm -dict 4871.dic -samprate 48000 -inmic yes -adcdev hw:0,0 -nfft 2048
pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm 4871.lm -dict 4871.dic -samprate 16000/8000/48000 -inmic yes -adcdev plughw:0,0 -logfn /dev/null -agc noise -nfft 4096 -vad_threshold 4
# -nfft 512
# -nfft 512 
# -nfft 2048 -agc noise -kws_threshold 1e-20



