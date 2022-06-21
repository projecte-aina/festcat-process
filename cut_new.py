import json
import os
import sys
import logging
import subprocess
from math import floor

def main():
    filename = sys.argv[1]
    indir = sys.argv[2]
    outdir = sys.argv[3]
    
    r = json.load(open(filename))
    results = r['results']
    for result in results:
        parse_and_segment(result, indir, outdir)

    with open(filename.replace('.json', '_m.json'), 'w') as out:
        json.dump(r, out, indent=2)

def parse_and_segment(result, indir, outdir):
    for i, cue in enumerate(result):
        if i == 0:
            cue['start'] = 0

        if i == len(result)-1:
            # in case len(result) == 0
            cue['end'] = cue['end']+3 # ffmpeg seeks the end

        if i > 0:
            # if there is one cue before
            cue['start'] -= (cue['start'] - result[i-1]['end'])/2

        if i < len(result)-1:
            # if there is one cue after
            cue['end'] += (result[i+1]['start'] - cue['end'])/2
        infile = '_'.join(os.path.basename(cue['segment']).split('_')[:-2])+'.wav'
        segment_cue(os.path.join(indir, infile), cue, outdir)

def segment_cue(audio, cue, base_path):
    audio_tool = 'ffmpeg'
    seek = floor(cue['start'])
    start = cue['start'] - seek
    end = cue['end']
    duration = end - cue['start']
    basename = '.'.join(os.path.basename(audio).split('.')[:-1])
    cue['segment'] = '_'.join([basename, '%3.3f'%cue['start'], '%3.3f'%cue['end']])
    cue['segment_path'] = os.path.join(base_path, cue['segment'])+'.wav'
    args = [audio_tool, '-y', '-hide_banner', '-loglevel', 'panic',\
            '-ss', str(seek), '-i', audio, '-ss', '%3.3f'%start, \
            '-t', '%3.3f'%duration, '-acodec', 'copy', \
            cue['segment_path']]
    if os.path.isfile(cue['segment_path']):
        logging.debug("%s already exists skipping"%cue['segment'])
    else:
        subprocess.call(args)
        if not os.path.isfile(cue['segment_path']):
            msg = "File not created from ffmpeg operation %s"\
                   %' '.join(args)
            logging.error(msg)
            raise IOError(msg)

if __name__ == "__main__":
    main()
