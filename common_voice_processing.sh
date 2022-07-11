#!/bin/bash
#SBATCH --job-name= ---
#SBATCH -D .
#SBATCH --output=.../common_voice.out
#SBATCH --error=.../common_voice.err
#SBATCH --gres=gpu:0
#SBATCH --nodes=1
#SBATCH -c 30
#SBATCH --time=2-0:00:00

export EXTRACT_PATH=".../extract_common_voice.py"
export TSV_PATH=".../validated.tsv"
export CV_PATH=".../ca/"
export PROCESS_AUDIO="True"
export N_P="50"
export SUMMARY="True"
export SPEAKERS_ID="[id_1, ..., id_n]"

python3 ${EXTRACT_PATH} --tsv-path ${TSV_PATH} --cv-path ${CV_PATH} --process-audio ${PROCESS_AUDIO} --summary ${SUMMARY} --n-p ${N_P}