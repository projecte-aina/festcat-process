for f in upc_ca_pau_raw/recordings/*.raw; do t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; done

for f in upc_ca_ona_raw/recordings/*.raw; do t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; done

mkdir upc_ca_pau_wav
mkdir upc_ca_pau_wav_22k
mkdir upc_ca_pau_wav_22k_sil
mkdir upc_ca_pau_wav_22k_sil_pad
for f in upc_ca_pau_raw/recordings/*.raw; do t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; done
for f in upc_ca_pau_wav/*.wav; do t=${f##*/}; ffmpeg -i $f -ar 22050 upc_ca_pau_wav_22k/$t -v error; done;
for f in upc_ca_pau_wav_22k/*.wav;do t=${f##*/}; sox $f upc_ca_pau_wav_22k_sil/$t silence 1 0.02 0.1% reverse silence 1 0.02 0.1% reverse; done
for f in upc_ca_pau_wav_22k_sil/*.wav;do t=${f##*/}; sox $f upc_ca_pau_wav_22k_sil_pad/$t pad 0 0.058; done

mkdir upc_ca_ona_wav
mkdir upc_ca_ona_wav_22k
mkdir upc_ca_ona_wav_22k_sil
mkdir upc_ca_ona_wav_22k_sil_pad
for f in upc_ca_ona_raw/recordings/*.raw; do t=${f%.raw}.wav; sox -t raw -r 48k -e signed -b 16 -c 1 $f $t; done
for f in upc_ca_ona_wav/*.wav; do t=${f##*/}; ffmpeg -i $f -ar 22050 upc_ca_ona_wav_22k/$t -v error; done;
for f in upc_ca_ona_wav_22k/*.wav;do t=${f##*/}; sox $f upc_ca_ona_wav_22k_sil/$t silence 1 0.02 0.5% reverse silence 1 0.02 0.5% reverse; done
for f in upc_ca_ona_wav_22k_sil/*.wav;do t=${f##*/}; sox $f upc_ca_ona_wav_22k_sil_pad/$t pad 0 0.058; done

utt dosyaları phoneme bazında timestampli
virgül nokta olan yerlerde normalde pau, pause oluyor, onlardan yararlanarak bölmek lazım
başlangıçta çok bekleme olanları var, audio dosyalarını filtrelerken bunu gözönünde bulundurmamış olabilirim

