import os
import re
import json
import argparse
import logging
import csv
import numpy as np

logger = logging.getLogger(__name__)

def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--tsv-path',
                       metavar='path',
                       type=str,
                       help='the path to tsv file')
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
    tsv_path = args.tsv_path
    wavs_path = args.wavs_path

    for locutor in locutors:
        # get durations
        durations = get_durations_dict(wavs_path + '%s_sil_stats.csv'%locutor)
        aggregate_duration = 0
        rejected_duration = 0
        large_duration = 0
        total_duration = 0
        tsv_name = "line_index_%s.tsv"%locutor
        tsv_path = tsv_path + tsv_name

        tsv_file = open(tsv_path)
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        files = []
        long_files = []
        for row in read_tsv:
            audio_filename = row[0] + ".wav"
            #logger.warning(f"Audio_filename {audio_filename}")
            sentence = row[-1]
            if sentence:
                target_path = 'ca_es_%s_22k_sil_pad'%locutor
                target_path = wavs_path + target_path
                source_filename = 'ca_es_%s_22k_sil/'%locutor+audio_filename ###
                source_filename = wavs_path + source_filename
                #logger.warning(f"source_filename {source_filename}")
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
        
        speakers_id = find_speakers_id(wavs_path + '%s_sil_stats.csv'%locutor)
        for id in speakers_id:
            speaker_file = files_spliter(files = files, speaker_id = id)
            if len(speaker_file) == 0:
                continue
            else:
                out(args, speaker_id = id, files = speaker_file)
                #print(f"mv {wavs_path}ca_{id}_test.txt  {wavs_path}{locutor}")
                #os.system(f"mv {wavs_path}ca_{id}_test.txt  {wavs_path}{locutor}")
                #os.system(f"mv {wavs_path}ca_{id}_val.txt  {wavs_path}{locutor}")
                #os.system(f"mv {wavs_path}ca_{id}_train.txt  {wavs_path}{locutor}")
        #out(args, locutor, files)
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

def out(args, speaker_id, files):

    #print(f"Length: {len(files)}")
    outname_length = [('ca_%s_test.txt'%speaker_id,0),
                      ('ca_%s_val.txt'%speaker_id,0),
                      ('ca_%s_train.txt'%speaker_id,len(files))]
    l_sum = sum([el[1] for el in outname_length])
    if len(files) != l_sum:
        msg = 'train vs test val distribution wrong: %i'%l_sum
        raise ValueError('msg')

    for fout, l in outname_length:
        open((args.wavs_path + fout), mode= 'a').close()
        #logger.warning(f"fout: {fout}")
        #logger.warning(f"l: {l}")
        with open((args.wavs_path + fout), 'w') as out:
            for i in range(l):
                f, sentence = files.pop()
                out.write('%s|%s\n'%(f.split("/")[-1].split(".")[-2],sentence))
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
    source = args.wavs_path +'ca_es_%s_22k_sil/'%locutor
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

def find_speakers_id(path_tsv):
  durations = {}
  for line in open(path_tsv).readlines():
      d = line.split(',')
      durations[d[0].split('/')[1]] = float(d[1])
  keysList = list(durations.keys())

  for index in range(len(keysList)):
    keysList[index] = keysList[index].split("_")[1]
  keysList = np.ndarray.tolist(np.unique(np.array(keysList)))
  return keysList

def files_spliter(files, speaker_id):
  out_file = []
  for element in files:
   # print(element[0].split("/")[-1].split("_")[1])
    if element[0].split("/")[-1].split("_")[1] == speaker_id:
      out_file.append(element)
  #print(out_file)
  return out_file

if __name__ == "__main__":
    main()

