import os
import re
import json
import subprocess

def main():
    for locutor in ['pau', 'ona']:
        # get durations
        #durations = get_durations_dict('%s_size.csv'%locutor)
        durations = get_durations_dict('%s_sil_stats.csv'%locutor)
        aggregate_duration = 0
        rejected_duration = 0
        large_duration = 0
        total_duration = 0

        path = 'upc_ca_%s_utt/utt'%locutor
        files = []
        long_files = []
        for filename in os.listdir(path):
            sentence = get_sentence(os.path.join(path, filename))
            audio_filename = filename.replace('.utt','.wav')
            if sentence:
                target_path = '/content/adaptation_%s_wav'%locutor
                target_filename = 'adaptation_%s_wav/'%locutor+audio_filename
                source_filename = 'adaptation_%s_full_wav/'%locutor+audio_filename
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
        #out(locutor, files)
        #out_long(locutor, long_files)
        #out_long_json(locutor, long_files)
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

def out(locutor, files):
    outname_length = [('upc_%s_test.txt'%locutor,0),
                      ('upc_%s_val.txt'%locutor,100),
                      ('upc_%s_train.txt'%locutor,len(files)-100)]
    l_sum = sum([el[1] for el in outname_length])
    if len(files) != l_sum:
        msg = 'train vs test val distribution wrong: %i'%l_sum
        raise ValueError('msg')

    for fout, l in outname_length:
        with open(fout, 'w') as out:
            for i in range(l):
                f, sentence = files.pop()
                out.write('%s|%s\n'%(f,sentence))
    print(len(files))

def out_long(locutor, files):
    outname = '%s_longsentences.csv'%locutor
    with open(outname, 'w') as out:
        for audio, text in files:
            out.write('%s,"%s"\n'%(audio, text))

def out_long_json(locutor, files):
    outname = '%s_longsentences.json'%locutor
    source = '/home/baybars/data/raw/festcat/adaptation_%s_full_wav'%locutor
    interventions = []
    for audio, text in files:
        intervention = {}
        intervention['text'] = [(locutor, text)]
        intervention['urls'] = [(locutor, os.path.join(source,audio))]
        interventions.append(intervention)

    with open(outname, 'w') as out:
        json.dump({'session': interventions}, out, indent=2)

if __name__ == "__main__":
    main()

