#!/bin/bash

if [ $# -ne 3 ]; then
    echo "usage  : $0 <data_dir> <new_srilm_dir> <wiki_clean_text_file>"
    echo "example: $0 data  data/srilm_wiki wiki_dump/clean_data.txt"
    exit;
fi

data=$1
old_lm_dir=$1/srilm

mkdir -p $2
new_lm_dir=$2

wiki_f=$3

if [ ! -d ${old_lm_dir} ]; then
    echo "${old_lm_dir} not found."
    exit;
fi

if [ -f ${new_lm_dir}/lm.gz ]; then
    echo "lm.gz already found in new LM dir: ${new_lm_dir}"
    exit;
fi

# copy LM txt files
for f in train.txt dev.txt vocab; do
    cp ${old_lm_dir}/$f ${new_lm_dir}/
done

# concatenate wiki and orig train data
cat ${old_lm_dir}/train.txt $wiki_f > ${new_lm_dir}/train.txt

# train LM
local/train_lms_srilm_wiki.sh ${new_lm_dir}

# copy lang dir
cp -r ${data}/lang ${data}/lang_wiki

# remove G.fst from the copied dir
rm -f ${data}/lang_wiki/G.fst

# create G.fst from lm.gz
local/arpa2G.sh ${new_lm_dir}/lm.gz ${data}/lang_wiki ${data}/lang_wiki

# make graph
utils/mkgraph.sh ${data}/lang_wiki exp_mfcc/tri5 exp_mfcc/tri5/graph_wiki

# Decoding with tri5 GMM model
for set_name in dev test; do

    if [ ! -f exp_mfcc/tri5/decode_${set_name}_wiki/.done ]; then
        echo ---------------------------------------------------------------------
        echo "Decoding ${set_name} using exp_mfcc/tri5 on" `date`
        echo ---------------------------------------------------------------------

        steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
                              --skip-scoring true \
                              exp_mfcc/tri5/graph_wiki ${data}/$set_name \
                              exp_mfcc/tri5/decode_${set_name}_wiki

        touch exp_mfcc/tri5/decode_${set_name}_wiki/.done

        local/score_kaldi.sh --cmd run.pl \
                             ${data}/${set_name} \
                             ${data}/lang_wiki \
                             exp_mfcc/tri5/decode_${set_name}_wiki/
    fi

done
