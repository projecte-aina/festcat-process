# Festcat data processing
Scripts to process festcat data, to make them compatible with training of modern TTS architectures

## Requirements
`sox`, `ffmpeg`

## Processing steps

0) Convert the files into 22050 Hz and remove the trailing silences
```
mkdir upc_ca_pau_wav
mkdir upc_ca_pau_wav_22k
mkdir upc_ca_pau_wav_22k_sil
mkdir upc_ca_pau_wav_22k_sil_pad
for f in upc_ca_pau_raw/recordings/*.raw; do t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; done
for f in upc_ca_pau_wav/*.wav; do t=${f##*/}; ffmpeg -i $f -ar 22050 upc_ca_pau_wav_22k/$t -v error; done;
for f in upc_ca_pau_wav_22k/*.wav;do t=${f##*/}; sox $f upc_ca_pau_wav_22k_sil/$t silence 1 0.02 0.1% reverse silence 1 0.02 0.1% reverse; done
```
Change the name pau to the actual speaker

1) Generate the duration file:
```
for f in upc_ca_pau_wav_22k_sil/*.wav; do d=`ffprobe -i $f -show_entries format=duration -v quiet -of csv="p=0"`; echo $f,$d; done
```

2) Put (or soft link) the utt path of the speaker to the top path in the repository

3) Run `python extract.py`

4) Add silence padding to files
```
for f in upc_ca_pau_wav_22k_sil/*.wav;do t=${f##*/}; sox $f upc_ca_pau_wav_22k_sil_pad/$t pad 0 0.058; done
```