import sys
import os
import shutil
import csv
import fnmatch
import subprocess
import argparse
import pandas as pd
import numpy as np
import multiprocessing
import time
import logging
logger = logging.getLogger(__name__)



def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--process-audio',
                       metavar='path',
                       type=bool,
                       default=False,
                       help='If True, it preprocess audiofiles and creates sil_stats.csv')
    my_parser.add_argument('--speakers-id',
                       metavar='path',
                       type=str,
                       default='all',
                       help='List of speakers IDs to be processaed. If None, it will process all the speakers')
    my_parser.add_argument('--summary',
                       metavar='path',
                       type=bool,
                       default=False,
                       help='If True, it performs a summary of the speakers')
    my_parser.add_argument('--tsv-path',
                       metavar='path',
                       required=True,
                       type=str,
                       help='the absolute path to validated.tsv file')
    my_parser.add_argument('--cv-path',
                       metavar='path',
                       required=True,
                       type=str,
                       help='the path to common-voice folder')
    my_parser.add_argument('--n-p',
                       metavar='path',
                       required=True,
                       default=30,
                       type=int,
                       help='Number of processes')
    args = my_parser.parse_args()
    tsv_path = args.tsv_path
    cv_path = args.cv_path
    summary = args.summary
    process_audio = args.process_audio
    speakers_list = args.speakers_id
    n_p = args.n_p

    if process_audio == True:
        start_time = time.perf_counter()
        processes = []
        subfolder_size = len(fnmatch.filter(os.listdir("%sclips"%cv_path), '*.mp3'))
        subfolder_size = subfolder_size // n_p
        subfolder_rest = (len(fnmatch.filter(os.listdir("%sclips"%cv_path), '*.mp3')) % n_p)
        subprocess.call(["mkdir","%sall_clips_wav_22k_sil_pad"%cv_path])
        process_index = []
        for i in range(n_p):
            if i == (n_p - 1):
                subfolder_size = subfolder_size + subfolder_rest
            subprocess.call(["mkdir", cv_path+"clips_"+str(i)])
            subprocess.call(["mkdir", cv_path+"clips_wavs_"+str(i)])
            subprocess.call(["mkdir","%sclips_wav_%s_22k"%(cv_path,str(i))])
            subprocess.call(["mkdir","%sclips_wav_%s_22k_sil"%(cv_path,str(i))])
            cmd = 'find '+'%sclips/'%cv_path +' -maxdepth 1 -type f '+'|head -%s|'%str(subfolder_size) +'xargs mv -t '+'"%sclips_%s"'%(cv_path, str(i))
            subprocess.call(cmd, shell=True)
            process_index.append((cv_path,str(i)))



        time_start = time.time()
        # Create pool of workers
        pool = multiprocessing.Pool(n_p)

        # Map pool of workers to process
        pool.starmap(func=AudioProcessing, iterable=process_index)

        # Wait until workers complete execution
        pool.close()

        time_end = time.time()
        print(f"Time elapsed: {round(time_end - time_start, 2)}s")
        # Creates n_p processes then starts them
        #for i in range(n_p):
        #    p = multiprocessing.Process(target = AudioProcessing(cv_path = cv_path, sub_number = str(i)))
        #    p.start()
        #    processes.append(p)

        # Joins all the processes 
        #for p in processes:
        #    p.join()

        join_sil_states(cv_path = cv_path, n_p = n_p)

        cmd_1 = "rm -r %sclips_*"%cv_path
        subprocess.call(cmd_1, shell=True)
        cmd_2 = "rm -r %ssil_stats_*"%cv_path
        subprocess.call(cmd_2, shell=True)
        finish_time = time.perf_counter()
        print(f"Processing finished in {finish_time-start_time} seconds")
    
    if summary == True:
        df = pd.read_csv(tsv_path, sep='\t')
        df, male_df, female_df, other_df, nan_df = split_df_by_gender(df)

        durations = get_durations_dict(cv_path + 'sil_stats.csv')
        for gender in ['male','female','other','nan']:
            if gender == 'male':
                df_ = male_df
                print("Processing male data, this can take few minutes")
            elif gender == 'female':
                df_ = female_df
                print("Processing female data, this can take few minutes")
            elif gender == 'other':
                df_ = other_df
                print("Processing other data, this can take few minutes")
            else:
                df_ = nan_df
                print("Processing nan data, this can take few minutes")
            open(f'{cv_path}{gender}.tsv', mode= 'a').close()
            speakers = np.ndarray.tolist(df_['client_id'].unique())
            d_speakers = dict.fromkeys(speakers,[0, 0, "", ""])
            with open(f'{cv_path}{gender}.tsv', mode= 'wt') as f:
                tsv_writer = csv.writer(f, delimiter='\t')
                tsv_writer.writerow(['client_id', 'time', 'number of samples', 'accent', 'age'])
                for key, value in durations.items():
                    if key.split('.')[0]+'.mp3' in df_.values:
                        client_id_ = df_.loc[df_['path'] == key.split('.')[0]+'.mp3']['client_id'].values[0]
                        client_id_ = str(client_id_)
                        age = df_.loc[df_['path'] == key.split('.')[0]+'.mp3']['age'].values[0]
                        accent = df_.loc[df_['path'] == key.split('.')[0]+'.mp3']['accents'].values[0]
                        #print(f"Before: {d_speakers[client_id_]}")
                        d_speakers[client_id_] = [d_speakers[client_id_][0] + value, d_speakers[client_id_][-3] , d_speakers[client_id_][-2], d_speakers[client_id_][-1]]
                        d_speakers[client_id_] = [d_speakers[client_id_][0], d_speakers[client_id_][-3] + 1, d_speakers[client_id_][-2], d_speakers[client_id_][-1]]
                        #print(f"After: {d_speakers[client_id_]}")

                        if type(d_speakers[client_id_][-2]) == float:
                            d_speakers[client_id_] = [d_speakers[client_id_][0],d_speakers[client_id_][-3],'', d_speakers[client_id_][-1]]
                        if type(accent) != float and d_speakers[client_id_][-2] == '':
                            d_speakers[client_id_] = [d_speakers[client_id_][0],d_speakers[client_id_][-3],accent, d_speakers[client_id_][-1]]
                        if type(d_speakers[client_id_][-1]) == float:
                            d_speakers[client_id_] = [d_speakers[client_id_][0],d_speakers[client_id_][-3],d_speakers[client_id_][-2], '']
                        if type(age) != float and d_speakers[client_id_][-1] == '':
                            d_speakers[client_id_] = [d_speakers[client_id_][0],d_speakers[client_id_][-3],d_speakers[client_id_][-2], age]
                    else:
                        continue
                d_speakers = dict(sorted(d_speakers.items(), key=lambda item: item[1]))
                print("Writting .tsv file")
                for key, value in d_speakers.items():
                    tsv_writer.writerow([key, value[0],  value[-3], value[-2].encode("ISO-8859-1"), value[-1].encode("ISO-8859-1")])
    else:
        if speakers_list == 'all':
            speakers_list = np.ndarray.tolist(pd.read_csv(tsv_path, sep='\t')['client_id'].unique())
        else:
            speakers_list = speakers_list.replace('[','').replace(']','').replace('"','').split(',')

        df = pd.read_csv(tsv_path, sep='\t', encoding = "ISO-8859-1")
        #df = pd.read_csv(tsv_path, sep='\t')
        durations = get_durations_dict(cv_path + 'sil_stats.csv')
        for id in speakers_list:
            files = []
            df_ = df[df['client_id'] == id]
            for index, row in df_.iterrows():
                if row['path'].split('.')[0]+'.wav' in durations:
                    files.append((row['path'].split('.')[0]+'.wav', row['sentence']))
                    #print(f"{row['path'].split('.')[0]+'.wav'}|{row['sentence']}")
                else:
                    continue
            out(cv_path = cv_path, speaker_id = id, files = files)

def get_durations_dict(filename):
    durations = {}
    for line in open(filename).readlines():
        d = line.split(',')
        if d[1]=='N/A\n':
            continue
        if float(d[1]) > 10: # Discard samples bigger than 10s 
            continue
        durations[d[0].split('/')[-1]] = float(d[1])
    return durations

def AudioProcessing(cv_path, sub_number):
        root_path = '/' + cv_path.split('/')[1]
        cmd_1 = "for f in %sclips_%s/*.mp3;"%(cv_path,sub_number) +" do t=${f%.mp3}.wav;"+" g=%sclips_wavs_%s/${t#%s*/clips_%s/}"%(cv_path,sub_number,root_path,sub_number) +"; mv $f $g; done"
        #subprocess.call(cmd_1, shell=True)
        os.system(cmd_1)
        cmd_2 = "for f in %sclips_wavs_%s/*.wav; do t=${f##*/}; ffmpeg -i $f -ar 22050 %sclips_wav_%s_22k/$t -v error < /dev/null; done;"%(cv_path, sub_number , cv_path, sub_number)
        os.system(cmd_2)
        #subprocess.call(cmd_2, shell=True)
        cmd_3 = "for f in %sclips_wav_%s_22k/*.wav; do t=${f##*/}; sox $f %sclips_wav_%s_22k_sil/$t"%(cv_path, sub_number , cv_path, sub_number) + " silence 1 0.02 0.1% reverse silence 1 0.02 0.1% reverse; done"
        os.system(cmd_3)
        #subprocess.call(cmd_3, shell=True)
        cmd_4 = "for f in %sclips_wav_%s_22k_sil/*.wav; do d=`ffprobe -i $f -show_entries format=duration -v quiet -of csv="%(cv_path,sub_number) +'"p=0"'+"`; echo $f,$d; done >> %ssil_stats_%s.csv"%(cv_path,sub_number)
        os.system(cmd_4)
        #subprocess.call(cmd_4, shell=True)
        #cmd_5 = "for f in %sclips_wav_%s_22k_sil/*.wav; do t=${f##*/}; sox $f %sclips_wav_%s_22k_sil_pad/$t pad 0 0.058; done"%(cv_path, sub_number , cv_path, sub_number)
        cmd_5 = "for f in %sclips_wav_%s_22k_sil/*.wav; do t=${f##*/}; sox $f %sall_clips_wav_22k_sil_pad/$t pad 0 0.058; done"%(cv_path, sub_number , cv_path)
        #subprocess.call(cmd_5, shell=True)
        os.system(cmd_5)
        #shutil.rmtree("%sclips_wavs"%cv_path)
        #shutil.rmtree("%sclips_wav_22k"%cv_path)
        #shutil.rmtree("%sclips_wav_22k_sil"%cv_path)

def join_sil_states(cv_path, n_p):
    durations = {}
    for i in range(n_p):
        for line in open("%ssil_stats_%s.csv"%(cv_path,str(i))).readlines():
            d = line.split(',')
            if d[1]=='N/A\n':
                #durations[d[0].split('/')[-1]] = float('nan')
                durations[d[0]] = float('nan')
                continue
            durations[d[0]] = float(d[1])
            #durations[d[0].split('/')[-1]] = float(d[1])
    open(f'{cv_path}sil_stats.csv', mode= 'a').close()
    with open(f'{cv_path}sil_stats.csv', mode= 'wt') as f:
        tsv_writer = csv.writer(f, delimiter=',')
        for key, value in durations.items():
            tsv_writer.writerow([key, value])

def split_df_by_gender(dataset):

    print(f"Total raws:  {(dataset.shape[0])}")
    
    non_gender_specified_raws = len(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'male']['client_id'].unique())) \
        + len(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'female']['client_id'].unique())) + \
            len(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'other']['client_id'].unique()))

    print(f"Number of raws withouth the known gender written {non_gender_specified_raws}")

    print("Correcting...")    
    for user in np.ndarray.tolist(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'male']['client_id'].unique())):
        dataset['gender'] = dataset['gender'].where((dataset['client_id'] != user), 'male')
    print("Correcting...")
    for user in np.ndarray.tolist(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'female']['client_id'].unique())):
        dataset['gender'] = dataset['gender'].where((dataset['client_id'] != user), 'female')
    print("Correcting...")
    for user in np.ndarray.tolist(np.intersect1d(dataset[dataset['gender'].isnull()]['client_id'].unique(), dataset[dataset['gender'] == 'other']['client_id'].unique())):
        dataset['gender'] = dataset['gender'].where((dataset['client_id'] != user), 'other')
    print("Corrected.")

    male = dataset[dataset['gender'] == 'male']
    female = dataset[dataset['gender'] == 'female']
    nan = dataset[dataset['gender'].isnull()]
    other = dataset[dataset['gender'] == 'other']
    print("----------Summary---------")
    print(f"Male raws:   {male.shape[0]}")
    print(f"Female raws: {female.shape[0]}")
    print(f"Other raws:  {other.shape[0]}")
    print(f"NaN raws:    {nan.shape[0]}    +")
    print("--------------------------")
    result = male.shape[0] + female.shape[0] + other.shape[0] + nan.shape[0]
    error = dataset.shape[0] - result
    print(f"             {result}     <--> Total raws:  {(dataset.shape[0])} (error: {error})")
    return dataset, male, female, other, nan

def out(cv_path, speaker_id, files):
    #print(f"Length: {len(files)}")
    outname_length = [('ca_%s_test.txt'%speaker_id,0),
                      ('ca_%s_val.txt'%speaker_id,0),
                      ('ca_%s_train.txt'%speaker_id,len(files))]
    l_sum = sum([el[1] for el in outname_length])
    if len(files) != l_sum:
        msg = 'train vs test val distribution wrong: %i'%l_sum
        raise ValueError('msg')

    for fout, l in outname_length:
        open((cv_path + fout), mode= 'a').close()
        #logger.warning(f"fout: {fout}")
        #logger.warning(f"l: {l}")
        with open((cv_path + fout), 'w') as out:
            for i in range(l):
                f, sentence = files.pop()
                out.write('%s|%s\n'%(f.split("/")[-1].split(".")[-2], sentence))
    print(len(files))

if __name__ == "__main__":
    main()