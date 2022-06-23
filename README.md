# Festcat data processing
Scripts to process festcat data, to make them compatible with training of modern TTS architectures

## Requirements
`sox`, `ffmpeg`

## Processing steps

1) Clone this repository:
```bash
git clone git@github.com:projecte-aina/festcat-process.git
```

2) Open the shell script [festcat_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/festcat_processing.sh) and modify the following variables:

```bash
export SPEAKER_NAME=...         # Speaker name or ID
export EXTRACT_PATH=...         # Absolute path to the script "extract.py"
export WAVS_PATH=...            # Path to where the "upc_ca_pep_raw" folder is located. (It must end with /)
export UTTERANCE_PATH=...       # Path to where the "upc_ca_pep_utt" folder is located. (It must end with /)
```

3) Run the shell script [festcat_processing.sh](https://github.com/projecte-aina/festcat-process/blob/main/festcat_processing.sh) from the directory where "upc_ca_speaker_raw" and "upc_ca_speaker_utt" are located.
