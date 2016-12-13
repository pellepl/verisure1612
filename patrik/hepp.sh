#!/usr/bin/env bash

pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm 0625.lm -dict 0625.dic -samprate 16000 -inmic yes -adcdev plughw:1,0 -nfft 2048 -logfn /dev/null

#pocketsphinx_continuous -hmm /usr/local/share/pocketsphinx/model/en-us/en-us -lm 0625.lm -dict 0625.dic -samprate 16000 -inmic yes -adcdev plughw:1,0 -nfft 2048 -keyphrase 'someone'
