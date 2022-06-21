import json
import sys
import os

def main():
    filename = sys.argv[1]
    locutor = filename.split('_')[0]
    r = json.load(open(filename))
    deleted = 0
    basepath = '/content/adaptation_%s_wav/'%locutor
    with open('upc_%s_train_add.txt'%locutor, 'w') as out:
        for result in r['results']:
            for cue in result:
                duration = cue['end'] - cue['start']
                if duration > 3:
                    filename = os.path.join(basepath, cue['segment'])+'.wav'
                    out.write('%s|%s\n'%(filename, cue['original_words']))
                else:
                    deleted += duration
    print(duration)

if __name__ == "__main__":
    main()
