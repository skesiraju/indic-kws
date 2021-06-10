#!/usr/bin/env bash
dir=exp_mfcc/tri6_nnet
train_stage=-10

dnn_mixup=5000
dnn_init_learning_rate=0.005
dnn_final_learning_rate=0.0005
dnn_num_hidden_layers=5

train_nj=1
decode_nj=20

export CUDA_VISIBLE_DEVICES=0


. conf/common_vars.sh
#. ./lang.conf

# This parameter will be used when the training dies at a certain point.
train_stage=-100
. ./utils/parse_options.sh

set -e
set -o pipefail
set -u

# Wait till the main run.sh gets to the stage where's it's
# finished aligning the tri5 model.
# echo "Waiting till exp/tri5_ali_train/.done exists...."
if [ ! -f exp_mfcc/tri5_ali/.done ]; then
    echo "exp_mfcc/tri5_ali/.done not found."
    exit;
fi

dnn_mem_reqs="mem_free=1.0G,ram_free=1.0G"
dnn_extra_opts="--num_epochs 20 --num-epochs-extra 10 --add-layers-period 1"

echo "extra opts: ""${dnn_extra_opts[@]}"

train_cmd="run.pl --gpu 0 --use-gpu wait"
decode_cmd="run.pl"

if [ ! -f $dir/.done ]; then

    echo ---------------------------------------------------------------------
    echo "Starting exp_mfcc/tri6_nnet on" `date`
    echo ---------------------------------------------------------------------

    steps/nnet2/train_tanh_fast.sh \
        --stage $train_stage --mix-up $dnn_mixup \
        --initial-learning-rate $dnn_init_learning_rate \
        --final-learning-rate $dnn_final_learning_rate \
        --num-hidden-layers $dnn_num_hidden_layers \
        --num-jobs-nnet ${train_nj} \
        --num_epochs 20 \
        --num-epochs-extra 10 \
        --add-layers-period 1 \
        --cmd "$train_cmd" \
        --num-threads 1 \
        --minibatch-size 128 \
        data/train data/lang exp_mfcc/tri5_ali $dir || exit 1

    touch $dir/.done
fi

for set_name in dev test; do

    if [ ! -f exp_mfcc/${dir}/decode_${set_name}/.done ]; then
        echo ---------------------------------------------------------------------
        echo "Decoding ${set_name} using ${dir} on" `date`
        echo ---------------------------------------------------------------------


        steps/nnet2/decode.sh --cmd "$decode_cmd" --nj "$decode_nj" \
                              --transform-dir exp_mfcc/tri5/decode_${set_name} \
                              exp_mfcc/tri5/graph data/${set_name} \
                              ${dir}/decode_${set_name}

        local/score_kaldi.sh --cmd run.pl data/${set_name} \
                             data/lang ${dir}/decode_${set_name}

        touch ${dir}/decode_${set_name}/.done
    fi

done
