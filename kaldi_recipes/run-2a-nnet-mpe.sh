#!/usr/bin/env bash

. conf/common_vars.sh
. cmd.sh
#. ./lang.conf

set -e
set -o pipefail
set -u

exp=exp_mfcc

# Wait for cross-entropy training.
# echo "Waiting till exp/tri6_nnet/.done exists...."
if [ ! -f ${exp}/tri6_nnet/.done ]; then
    echo "Not found exp/tri6_nnet/.done"
    exit;
fi

train_nj=5
decode_nj=20

export CUDA_VISIBLE_DEVICES=0


# Generate denominator lattices.
if [ ! -f ${exp}/tri6_nnet_denlats/.done ]; then
    steps/nnet2/make_denlats.sh "${dnn_denlats_extra_opts[@]}" \
                                --nj $train_nj --sub-split $train_nj \
                                --transform-dir ${exp}/tri5_ali \
                                data/train \
                                data/lang \
                                ${exp}/tri6_nnet \
                                ${exp}/tri6_nnet_denlats || exit 1

    touch ${exp}/tri6_nnet_denlats/.done
fi

# alignments for train
if [ ! -f ${exp}/tri6_nnet_ali/.done ]; then

    steps/nnet2/align.sh --use-gpu wait \
                         --cmd "$decode_cmd" \
                         --transform-dir ${exp}/tri5_ali --nj $train_nj \
                         data/train data/lang ${exp}/tri6_nnet ${exp}/tri6_nnet_ali || exit 1

    touch ${exp}/tri6_nnet_ali/.done
fi

# Generate alignments for dev and test
for set_name in dev test; do

    if [ ! -f ${exp}/tri6_nnet_ali_${set_name}/.done ]; then

        steps/nnet2/align.sh --use-gpu wait \
                             --cmd "$decode_cmd" \
                             --transform-dir ${exp}/tri5_ali_${set_name} \
                             --nj $train_nj \
                             data/${set_name} data/lang ${exp}/tri6_nnet ${exp}/tri6_nnet_ali_${set_name} || exit 1

        touch ${exp}/tri6_nnet_ali_${set_name}/.done
    fi
done

criterion=smbr
train_stage=-100

if [ ! -f ${exp}/tri6_nnet_${criterion}/.done ]; then

    steps/nnet2/train_discriminative.sh \
        --stage $train_stage --cmd "$cuda_cmd" \
        --num-threads 1 \
        --criterion $criterion \
        --modify-learning-rates true \
        --num-epochs 4 --cleanup true \
        --transform-dir ${exp}/tri5_ali \
        data/train data/lang \
        ${exp}/tri6_nnet_ali \
        ${exp}/tri6_nnet_denlats \
        ${exp}/tri6_nnet/final.mdl \
        ${exp}/tri6_nnet_${criterion} || exit 1

    touch ${exp}/tri6_nnet_${criterion}/.done
fi

dir=${exp}/tri6_nnet_${criterion}

for set_name in dev test; do

    echo "${dir}/decode_${set_name}/.done"
    if [ ! -f ${dir}/decode_${set_name}/.done ]; then
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

# Generate alignments for dev and test
for set_name in dev test; do

    if [ ! -f ${exp}/tri6_nnet_${criterion}_ali_${set_name}/.done ]; then

        echo ---------------------------------------------------------------------
        echo "Aligning ${set_name} using ${dir} on" `date`
        echo ---------------------------------------------------------------------

        steps/nnet2/align.sh --use-gpu wait \
                             --cmd "$decode_cmd" \
                             --transform-dir ${exp}/tri5_ali_${set_name} \
                             --nj $train_nj \
                             data/${set_name} \
                             data/lang \
                             ${exp}/tri6_nnet_${criterion} \
                             ${exp}/tri6_nnet_${criterion}_ali_${set_name} || exit 1

        touch ${exp}/tri6_nnet_${criterion}_ali_${set_name}/.done
    fi
done
