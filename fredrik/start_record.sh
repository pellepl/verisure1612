#!/bin/bash
echo "Start recording..."
arecord -D plughw:0,0 -f cd ./myrec_16khz.wav
#rec -r 16000 -c 1 -d 3 ./myrec_16khz_mono.wav
echo "Coverting..."
sox ./myrec_16khz.wav -c 1 -r 16000 ./myrec_16khz_mono.wav
echo "Done!"
