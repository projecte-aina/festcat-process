#!/bin/sh

export SPEAKER_NAME="male"
export OUTPUT_CSV="${SPEAKER_NAME}_sil_stats.csv"
export EXTRACT_PATH="/home/usuaris/scratch/gerard.muniesa/extract_google_tts.py"
export WAVS_PATH="/home/usuaris/scratch/gerard.muniesa/google_tts/"
export TSV_PATH="/home/usuaris/scratch/gerard.muniesa/google_tts/"

mkdir ${SPEAKER_NAME}

mkdir ca_es_${SPEAKER_NAME}_22k
mkdir ca_es_${SPEAKER_NAME}_22k_sil
mkdir ca_es_${SPEAKER_NAME}_22k_sil_pad

for f in ca_es_${SPEAKER_NAME}/*.wav; do
t=${f##*/}; ffmpeg -i $f -ar 22050 ca_es_${SPEAKER_NAME}_22k/$t -v error < /dev/null; 
done;

for f in ca_es_${SPEAKER_NAME}_22k/*.wav; do 
t=${f##*/}; sox $f ca_es_${SPEAKER_NAME}_22k_sil/$t silence 1 0.02 0.1% reverse silence 1 0.02 0.1% reverse; 
done

for f in ca_es_${SPEAKER_NAME}_22k_sil/*.wav; do 
d=`ffprobe -i $f -show_entries format=duration -v quiet -of csv="p=0"`; 
echo $f,$d;
done >> ${OUTPUT_CSV}

python ${EXTRACT_PATH} --wavs-path ${WAVS_PATH} --tsv-path ${TSV_PATH} --locutors ${SPEAKER_NAME}

for f in ca_es_${SPEAKER_NAME}_22k_sil/*.wav; do 
t=${f##*/}; sox $f ca_es_${SPEAKER_NAME}_22k_sil_pad/$t pad 0 0.058; 
done

rm -r ca_es_${SPEAKER_NAME}_22k
rm -r ca_es_${SPEAKER_NAME}_22k_sil
mv ca_es_${SPEAKER_NAME}*  ${SPEAKER_NAME}
mv ca_${SPEAKER_NAME}* ${SPEAKER_NAME}
mv line_index_${SPEAKER_NAME}* ${SPEAKER_NAME}
mv ${SPEAKER_NAME}_* ${SPEAKER_NAME}