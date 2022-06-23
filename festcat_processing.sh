#!/bin/sh

export SPEAKER_NAME=...
export OUTPUT_CSV="${SPEAKER_NAME}_sil_stats.csv"
export EXTRACT_PATH=...
export WAVS_PATH=...
export UTTERANCE_PATH=...

mkdir ${SPEAKER_NAME}

mkdir upc_ca_${SPEAKER_NAME}_wav
mkdir upc_ca_${SPEAKER_NAME}_wav_22k
mkdir upc_ca_${SPEAKER_NAME}_wav_22k_sil
mkdir upc_ca_${SPEAKER_NAME}_wav_22k_sil_pad


for f in upc_ca_${SPEAKER_NAME}_raw/recordings/*.raw; do 
t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; 
done

mv upc_ca_${SPEAKER_NAME}_raw/recordings/*.wav  upc_ca_${SPEAKER_NAME}_wav/

for f in upc_ca_${SPEAKER_NAME}_wav/*.wav; do
t=${f##*/}; ffmpeg -i $f -ar 22050 upc_ca_${SPEAKER_NAME}_wav_22k/$t -v error < /dev/null; 
done;

for f in upc_ca_${SPEAKER_NAME}_wav_22k/*.wav; do 
t=${f##*/}; sox $f upc_ca_${SPEAKER_NAME}_wav_22k_sil/$t silence 1 0.02 0.1% reverse silence 1 0.02 0.1% reverse; 
done

for f in upc_ca_${SPEAKER_NAME}_wav_22k_sil/*.wav; do 
d=`ffprobe -i $f -show_entries format=duration -v quiet -of csv="p=0"`; 
echo $f,$d;
done >> ${OUTPUT_CSV}

python ${EXTRACT_PATH} --wavs-path ${WAVS_PATH} --utterance-path ${UTTERANCE_PATH} --locutors ${SPEAKER_NAME}

for f in upc_ca_${SPEAKER_NAME}_wav_22k_sil/*.wav; do 
t=${f##*/}; sox $f upc_ca_${SPEAKER_NAME}_wav_22k_sil_pad/$t pad 0 0.058; 
done

mv upc_ca_${SPEAKER_NAME}*  ${SPEAKER_NAME}
mv upc_${SPEAKER_NAME}* ${SPEAKER_NAME}
mv ${SPEAKER_NAME}_* ${SPEAKER_NAME}