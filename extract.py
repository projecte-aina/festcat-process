import os
import re
import json
import subprocess
import argparse
import logging

logger = logging.getLogger(__name__)

def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--utterance-path',
                       metavar='path',
                       type=str,
                       help='the path to utterance file')
    my_parser.add_argument('--wavs-path',
                       metavar='path',
                       type=str,
                       help='the path to wavs file')
    my_parser.add_argument('--locutors',
                       metavar='N',
                       type=str,
                       help='list of speakers names/id separated with commas')
    args = my_parser.parse_args()
    locutors = args.locutors
    locutors = locutors.replace(" ", "");
    locutors = locutors.split(",")
    utterance_path = args.utterance_path
    wavs_path = args.wavs_path

    for locutor in locutors:
        # get durations
        durations = get_durations_dict(wavs_path + '%s_sil_stats.csv'%locutor)
        aggregate_duration = 0
        rejected_duration = 0
        large_duration = 0
        total_duration = 0
        path = 'upc_ca_%s_utt/utt'%locutor
        path = utterance_path + path

        files = []
        long_files = []
        for filename in os.listdir(path):
            sentence = get_sentence(os.path.join(path, filename))
            audio_filename = filename.replace('.utt','.wav') # upc_ca_pep_203479.wav
            if sentence:
                target_path = 'filtered_%s_wav'%locutor
                target_path = wavs_path + target_path
                source_filename = 'upc_ca_%s_wav_22k_sil/'%locutor+audio_filename
                source_filename = wavs_path + source_filename
                total_duration += durations[audio_filename]

                if os.path.isfile(source_filename):
                    if durations[audio_filename] < 10.0:
                        aggregate_duration += durations[audio_filename]
                        files.append((os.path.join(target_path,audio_filename), sentence))
                        #subprocess.call(['cp',source_filename, target_filename])
                    else:
                        long_files.append((audio_filename, sentence))
                        large_duration += durations[audio_filename]
                else:
                    print(audio_filename)
            else:
                rejected_duration += durations[audio_filename]
        out(args, locutor, files)
        out_long(args, locutor, long_files)
        out_long_json(args, locutor, long_files)
        print(locutor, aggregate_duration/3600, 'hours')
        print(locutor, 'rejected due to duration', large_duration/3600, 'hours')
        print(locutor, 'rejected', rejected_duration/60, 'minutes')
        print(locutor, total_duration, aggregate_duration+rejected_duration+large_duration)

def get_durations_dict(filename):
    durations = {}
    for line in open(filename).readlines():
        d = line.split(',')
        durations[d[0].split('/')[1]] = float(d[1])
    return durations

def get_sentence(filename):
    utt_all = open(filename, encoding = "ISO-8859-1").read()
    m = re.search('(\"\\\\\")(.+)(\\\\\"\")', utt_all)
    sentence = m.groups()[1]
    # delete interword dashes
    sentence = re.sub('-(?=([A-Z]))', ' ', sentence)
    if not re.search('\d', sentence):
        return sentence
    else:
        print(filename, sentence)
        return None

def out(args, locutor, files):

    outname_length = [('upc_%s_test.txt'%locutor,0),
                      ('upc_%s_val.txt'%locutor,100),
                      ('upc_%s_train.txt'%locutor,len(files)-100)]
    l_sum = sum([el[1] for el in outname_length])
    if len(files) != l_sum:
        msg = 'train vs test val distribution wrong: %i'%l_sum
        raise ValueError('msg')

    for fout, l in outname_length:
        open((args.wavs_path + fout), mode= 'a').close()
        logger.warning(f"fout: {fout}")
        logger.warning(f"l: {l}")
        with open((args.wavs_path + fout), 'w') as out:
            for i in range(l):
                f, sentence = files.pop()
                out.write('%s|%s\n'%(f,sentence))
    print(len(files))

def out_long(args, locutor, files):
    outname = '%s_longsentences.csv'%locutor
    outname_path = args.wavs_path + outname
    open(outname_path, mode= 'a').close()
    with open(outname_path, 'w') as out:
        for audio, text in files:
            out.write('%s,"%s"\n'%(audio, text))

def out_long_json(args, locutor, files):
    outname = '%s_longsentences.json'%locutor
    source = args.wavs_path +'upc_ca_%s_wav_22k_sil/'%locutor
    outname_path = args.wavs_path + outname
    open(outname_path, mode= 'a').close()
    interventions = []
    for audio, text in files:
        intervention = {}
        intervention['text'] = [(locutor, text)]
        intervention['urls'] = [(locutor, os.path.join(source,audio))]
        interventions.append(intervention)
    
    with open(outname_path, 'w') as out:
        json.dump({'session': interventions}, out, indent=2)

if __name__ == "__main__":
    main()

