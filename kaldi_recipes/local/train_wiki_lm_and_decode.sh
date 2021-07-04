#!/bin/bash

if [ $# -le 3 ]; then
    echo "usage  : $0 <data_dir> <new_srilm_dir> <wiki_clean_text_file> [step: 1 to 5]"
    echo "example: $0 data  data/srilm_wiki wiki_dump/clean_data.txt 1"
    echo "step 1 : train lm on wiki"
    echo "step 2 : copy lang dir and arpa2G"
    echo "step 3 : mkgraph"
    echo "step 4 : decode using tri5 gmm"
    echo "step 5 : decode using tri6 nnet"
    echo "step 6 : decode using tri6 smbr"
    exit;
fi

data=$1
old_lm_dir=$1/srilm

mkdir -p $2
new_lm_dir=$2

wiki_f=$3
step=${4:-1}

decode_nj=20

if [ $step == 1 ]; then

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

elif [ $step == 2 ]; then

    # copy lang dir
    cp -r ${data}/lang ${data}/lang_wiki

    # remove G.fst from the copied dir
    rm -f ${data}/lang_wiki/G.fst

    # create G.fst from lm.gz
    local/arpa2G.sh ${new_lm_dir}/lm.gz ${data}/lang_wiki ${data}/lang_wiki

elif [ $step == 3 ]; then
    # make graph
    utils/mkgraph.sh ${data}/lang_wiki exp_mfcc/tri5 exp_mfcc/tri5/graph_wiki

elif [ $step == 4 ]; then

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


elif [ $step == 5 ]; then

    graph_dir=graph_wiki
    sfx="wiki"

    for set_name in dev test; do

        if [ ! -f exp_mfcc/${dir}/decode_${set_name}_${sfx}/.done ]; then
            echo ---------------------------------------------------------------------
            echo "Decoding ${set_name} using ${dir} on" `date`
            echo ---------------------------------------------------------------------

            steps/nnet2/decode.sh --cmd "$decode_cmd" --nj "$decode_nj" \
                                  --transform-dir exp_mfcc/tri5/decode_${set_name}_${sfx} \
                                  exp_mfcc/tri5/${graph_dir} data/${set_name} \
                                  exp_mfcc/tri6_nnet/decode_${set_name}_${sfx}

            local/score_kaldi.sh --cmd run.pl data/${set_name} \
                                 data/lang_${sfx} \
                                 exp_mfcc/tri6_nnet/decode_${set_name}_${sfx}

            touch exp_mfcc/tri6_nnet/decode_${set_name}_${sfx}/.done
        fi

    done

elif [ $step == 6 ]; then

    echo "Not implemented"
    graph_dir=exp_mfcc/tri5/graph_wiki
    sfx="wiki"


fi
