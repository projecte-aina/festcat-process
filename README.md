# Festcat & Google TTS data processing
Scripts to process [festcat](http://festcat.talp.cat/devel.php) and [google_tts](http://openslr.org/69/) data, to make them compatible with training of modern TTS architectures

## Requirements
`sox`, `ffmpeg`

## Festcat
### Processing steps

1) Clone this repository:
```bash
git clone git@github.com:projecte-aina/festcat-process.git
```

2) Open the shell script [festcat_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/festcat_processing.sh) and modify the following variables:

```bash
export SPEAKER_NAME=...         # Speaker name or ID
export EXTRACT_PATH=...         # Absolute path to the script "extract_festcat.py"
export WAVS_PATH=...            # Path to where the "upc_ca_(speaker_id)_raw" folder is located. (It must end with /)
export UTTERANCE_PATH=...       # Path to where the "upc_ca_(speaker_id)_utt" folder is located. (It must end with /)
```

3) Run the shell script [festcat_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/festcat_processing.sh) from the directory where "upc_ca_(speaker_id)_raw" and "upc_ca_(speaker_id)_utt" are located.

## Google TTS
### Processing steps

1) Clone this repository:
```bash
git clone git@github.com:projecte-aina/festcat-process.git
```

2) Open the shell script [google_tts_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/google_tts_processing.sh) and modify the following variables:

```bash
export SPEAKER_NAME=...         # Speaker name or ID
export EXTRACT_PATH=...         # Absolute path to the script "extract_google_tts.py"
export WAVS_PATH=...            # Path to where the "ca_es_(speaker_id)" folder is located. (It must end with /)
export TSV_PATH=...             # Path to where the "line_index_(speaker_id).tsv" file is located. (It must end with)
```

3) Run the shell script [google_tts_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/google_tts_processing.sh) from the directory where "ca_es_(speaker_id)" and "line_index_(speaker_id).tsv" are located.