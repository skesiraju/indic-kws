#!/usr/bin/env bash

tri5_only=true
sgmm5_only=false
data_only=false

[ ! -f ./conf/common_vars.sh ] && echo 'the file conf/common_vars.sh does not exist!' && exit 1

. conf/common_vars.sh || exit 1;

. ./utils/parse_options.sh

set -e           #Exit on non-zero return code from any command
set -o pipefail  #Exit if any of the commands in the pipeline will
                 #return non-zero return code
#set -u           #Fail on an undefined variable


train_nj=10
decode_nj=10


if [ ! -f data/train/.donexx ]; then

    echo ---------------------------------------------------------------------
    echo "Create spk2utt from utt2spk in train dev and test. Preparing lang"
    echo ---------------------------------------------------------------------

    grep -v -w sil data/local/dict/lexicon.txt | \
        awk '{for(n=2;n<=NF;n++) { p[$n]=1; }} END{for(x in p) {print x}}' | sort > data/local/dict/nonsilence_phones.txt
    echo sil > data/local/dict/silence_phones.txt
    echo sil > data/local/dict/optional_silence.txt
    touch data/local/dict/extra_questions.txt # no extra questions, as we have no stress or tone markers.

    utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
    utils/utt2spk_to_spk2utt.pl data/dev/utt2spk > data/dev/spk2utt
    utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt
    utils/prepare_lang.sh data/local/dict "<unk>" data/local/lang_test data/lang_no

    touch data/train/.donexx
fi

# We will simply override the default G.fst by the G.fst generated using SRILM
if [[ ! -f data/srilm/lm.gz || data/srilm/lm.gz -ot data/train/text ]]; then

    echo ---------------------------------------------------------------------
    echo "Training SRILM language models on" `date`
    echo ---------------------------------------------------------------------

    local/prepare_lm.sh
    utils/format_lm.sh data/lang_no data/local/lm.gz data/local/dict/lexicon.txt data/lang

    local/train_lms_srilm.sh --dev-text data/dev/text --train-text data/train/text data data/srilm
fi

if [[ ! -f data/lang/G.fst || data/lang/G.fst -ot data/srilm/lm.gz ]]; then
    echo ---------------------------------------------------------------------
    echo "Creating G.fst on " `date`
    echo ---------------------------------------------------------------------
    local/arpa2G.sh data/srilm/lm.gz data/lang data/lang
fi

mfccdir=mfcc

for set_name in train dev test; do


    if [ ! -f data/${set_name}/.mfcc.done ]; then

        echo ---------------------------------------------------------------------
        echo "Starting mfcc feature extraction for data/${set_name} in ${mfccdir} on" `date`
        echo ---------------------------------------------------------------------

        steps/make_mfcc.sh --cmd "$train_cmd" --nj 20 \
                           data/$set_name exp_mfcc/make_mfcc/$set_name $mfccdir || exit 1;

        utils/data/get_segments_for_data.sh data/${set_name} > data/${set_name}/segments

        utils/fix_data_dir.sh data/${set_name}
        steps/compute_cmvn_stats.sh data/${set_name} exp_mfcc/make_mfcc/${set_name} $mfccdir
        utils/fix_data_dir.sh data/${set_name}
        touch data/${set_name}/.mfcc.done
    fi

done


if [ ! -f data/train_sub3/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Subsetting monophone training data in data/train_sub[123] on" `date`
    echo ---------------------------------------------------------------------
    numutt=`cat data/train/feats.scp | wc -l`;
    utils/subset_data_dir.sh --shortest data/train 1000 data/train_sub1
    if [ $numutt -gt 5000 ] ; then
        utils/subset_data_dir.sh data/train 5000 data/train_sub2
    else
        (cd data; ln -s train train_sub2 )
    fi
    if [ $numutt -gt 10000 ] ; then
        utils/subset_data_dir.sh data/train 10000 data/train_sub3
    else
        (cd data; ln -s train train_sub3 )
    fi

    touch data/train_sub3/.done
fi


if $data_only; then
    echo "--data-only is true" && exit 0
fi


boost_sil=1.25
numLeavesTri1=2000
numGaussTri1=10000

numLeavesTri2=2000
numGaussTri2=10000

numLeavesTri3=2000
numGaussTri3=10000

numLeavesMLLT=2500
numGaussMLLT=15000

numLeavesSAT=2500
numGaussSAT=15000

if [ ! -f exp_mfcc/mono/.done ]; then

    echo ---------------------------------------------------------------------
    echo "Starting (small) monophone training in exp_mfcc/mono on" `date`
    echo ---------------------------------------------------------------------
    steps/train_mono.sh \
        --boost-silence $boost_sil --nj 8 --cmd "$train_cmd" \
        data/train_sub1 data/lang exp_mfcc/mono
    touch exp_mfcc/mono/.done
fi



if [ ! -f exp_mfcc/tri1/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting (small) triphone training in exp_mfcc/tri1 on" `date`
    echo ---------------------------------------------------------------------
    steps/align_si.sh \
        --boost-silence $boost_sil --nj 12 --cmd "$train_cmd" \
        data/train_sub2 data/lang exp_mfcc/mono exp_mfcc/mono_ali_sub2
    steps/train_deltas.sh \
        --boost-silence $boost_sil --cmd "$train_cmd" $numLeavesTri1 $numGaussTri1 \
        data/train_sub2 data/lang exp_mfcc/mono_ali_sub2 exp_mfcc/tri1
    touch exp_mfcc/tri1/.done
fi


if [ ! -f exp_mfcc/tri2/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting (medium) triphone training in exp_mfcc/tri2 on" `date`
    echo ---------------------------------------------------------------------

    steps/align_si.sh \
        --boost-silence $boost_sil --nj 24 --cmd "$train_cmd" \
        data/train_sub3 data/lang exp_mfcc/tri1 exp_mfcc/tri1_ali_sub3
    steps/train_deltas.sh \
        --boost-silence $boost_sil --cmd "$train_cmd" $numLeavesTri2 $numGaussTri2 \
        data/train_sub3 data/lang exp_mfcc/tri1_ali_sub3 exp_mfcc/tri2
    touch exp_mfcc/tri2/.done
fi


if [ ! -f exp_mfcc/tri3/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting (full) triphone training in exp_mfcc/tri3 on" `date`
    echo ---------------------------------------------------------------------
    steps/align_si.sh \
        --boost-silence $boost_sil --nj $train_nj --cmd "$train_cmd" \
        data/train data/lang exp_mfcc/tri2 exp_mfcc/tri2_ali
    steps/train_deltas.sh \
        --boost-silence $boost_sil --cmd "$train_cmd" \
        $numLeavesTri3 $numGaussTri3 data/train data/lang exp_mfcc/tri2_ali exp_mfcc/tri3
    touch exp_mfcc/tri3/.done
fi


if [ ! -f exp_mfcc/tri4/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting (lda_mllt) triphone training in exp_mfcc/tri4 on" `date`
    echo ---------------------------------------------------------------------
    steps/align_si.sh \
        --boost-silence $boost_sil --nj $train_nj --cmd "$train_cmd" \
        data/train data/lang exp_mfcc/tri3 exp_mfcc/tri3_ali
    steps/train_lda_mllt.sh \
        --boost-silence $boost_sil --cmd "$train_cmd" \
        $numLeavesMLLT $numGaussMLLT data/train data/lang exp_mfcc/tri3_ali exp_mfcc/tri4
    touch exp_mfcc/tri4/.done
fi


if [ ! -f exp_mfcc/tri5/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting (SAT) triphone training in exp_mfcc/tri5 on" `date`
    echo ---------------------------------------------------------------------

    steps/align_si.sh \
        --boost-silence $boost_sil --nj $train_nj --cmd "$train_cmd" \
        data/train data/lang exp_mfcc/tri4 exp_mfcc/tri4_ali
    steps/train_sat.sh \
        --boost-silence $boost_sil --cmd "$train_cmd" \
        $numLeavesSAT $numGaussSAT data/train data/lang exp_mfcc/tri4_ali exp_mfcc/tri5
    touch exp_mfcc/tri5/.done
fi


utils/mkgraph.sh data/lang exp_mfcc/tri5 exp_mfcc/tri5/graph


for set_name in dev test; do

    if [ ! -f exp_mfcc/tri5/decode_${set_name}/.done ]; then
        echo ---------------------------------------------------------------------
        echo "Decoding ${set_name} using exp_mfcc/tri5 on" `date`
        echo ---------------------------------------------------------------------

        steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
                              --skip-scoring true \
                              exp_mfcc/tri5/graph data/$set_name \
                              exp_mfcc/tri5/decode_$set_name
        touch exp_mfcc/tri5/decode_${set_name}/.done

        local/score_kaldi.sh --cmd run.pl \
                             data/${set_name} \
                             data/lang \
                             exp_mfcc/tri5/decode_${set_name}/
    fi

done

# align training data - will be used to train DNN

if [ ! -f exp_mfcc/tri5_ali/.done ]; then
    echo ---------------------------------------------------------------------
    echo "Starting exp_mfcc/tri5_ali on" `date`
    echo ---------------------------------------------------------------------
    steps/align_fmllr.sh \
        --boost-silence $boost_sil --nj $train_nj --cmd "$train_cmd" \
        data/train data/lang exp_mfcc/tri5 exp_mfcc/tri5_ali
    touch exp_mfcc/tri5_ali/.done
fi


# generate rttm for dev - because we need to run KWS
# for test data - only to see how better it is from earlier experiments

for set_name in dev test; do

    if [ ! -f exp_mfcc/tri5_ali_${set_name}/.done ]; then
        echo ---------------------------------------------------------------------
        echo "Aligning ${set_name} using exp_mfcc/tri5_ali_${set_name} on" `date`
        echo ---------------------------------------------------------------------

        steps/align_fmllr.sh  \
            --boost-silence $boost_sil --nj $train_nj --cmd "$train_cmd" \
            data/${set_name} data/lang exp_mfcc/tri5 exp_mfcc/tri5_ali_${set_name}

        touch exp_mfcc/tri5_ali_${set_name}/.done
    fi

done


exit;

# No need to do SGMM training

################################################################################
# Ready to start SGMM training
################################################################################


if $tri5_only ; then
  echo "Exiting after stage TRI5, as requested. "
  echo "Everything went fine. Done"
  exit 0;
fi

if [ ! -f exp_mfcc/ubm5/.done ]; then
  echo ---------------------------------------------------------------------
  echo "Starting exp_mfcc/ubm5 on" `date`
  echo ---------------------------------------------------------------------
  steps/train_ubm.sh \
    --cmd "$train_cmd" $numGaussUBM \
    data/train data/lang exp_mfcc/tri5_ali exp_mfcc/ubm5
  touch exp_mfcc/ubm5/.done
fi

if [ ! -f exp_mfcc/sgmm5/.done ]; then
  echo ---------------------------------------------------------------------
  echo "Starting exp_mfcc/sgmm5 on" `date`
  echo ---------------------------------------------------------------------
  steps/train_sgmm2.sh \
    --cmd "$train_cmd" $numLeavesSGMM $numGaussSGMM \
    data/train data/lang exp_mfcc/tri5_ali exp_mfcc/ubm5/final.ubm exp_mfcc/sgmm5
  #steps/train_sgmm2_group.sh \
  #  --cmd "$train_cmd" "${sgmm_group_extra_opts[@]-}" $numLeavesSGMM $numGaussSGMM \
  #  data/train data/lang exp_mfcc/tri5_ali exp_mfcc/ubm5/final.ubm exp_mfcc/sgmm5
  touch exp_mfcc/sgmm5/.done
fi

if $sgmm5_only ; then
  echo "Exiting after stage SGMM5, as requested. "
  echo "Everything went fine. Done"
  exit 0;
fi
################################################################################
# Ready to start discriminative SGMM training
################################################################################

if [ ! -f exp_mfcc/sgmm5_ali/.done ]; then
  echo ---------------------------------------------------------------------
  echo "Starting exp_mfcc/sgmm5_ali on" `date`
  echo ---------------------------------------------------------------------
  steps/align_sgmm2.sh \
    --nj $train_nj --cmd "$train_cmd" --transform-dir exp_mfcc/tri5_ali \
    --use-graphs true --use-gselect true \
    data/train data/lang exp_mfcc/sgmm5 exp_mfcc/sgmm5_ali
  touch exp_mfcc/sgmm5_ali/.done
fi


if [ ! -f exp_mfcc/sgmm5_denlats/.done ]; then
  echo ---------------------------------------------------------------------
  echo "Starting exp_mfcc/sgmm5_denlats on" `date`
  echo ---------------------------------------------------------------------
  steps/make_denlats_sgmm2.sh \
    --nj $train_nj --sub-split $train_nj "${sgmm_denlats_extra_opts[@]}" \
    --beam 10.0 --lattice-beam 6 --cmd "$decode_cmd" --transform-dir exp_mfcc/tri5_ali \
    data/train data/lang exp_mfcc/sgmm5_ali exp_mfcc/sgmm5_denlats
  touch exp_mfcc/sgmm5_denlats/.done
fi

if [ ! -f exp_mfcc/sgmm5_mmi_b0.1/.done ]; then
  echo ---------------------------------------------------------------------
  echo "Starting exp_mfcc/sgmm5_mmi_b0.1 on" `date`
  echo ---------------------------------------------------------------------
  steps/train_mmi_sgmm2.sh \
    --cmd "$train_cmd" "${sgmm_mmi_extra_opts[@]}" \
    --drop-frames true --transform-dir exp_mfcc/tri5_ali --boost 0.1 \
    data/train data/lang exp_mfcc/sgmm5_ali exp_mfcc/sgmm5_denlats \
    exp_mfcc/sgmm5_mmi_b0.1
  touch exp_mfcc/sgmm5_mmi_b0.1/.done
fi

echo ---------------------------------------------------------------------
echo "Finished successfully on" `date`
echo ---------------------------------------------------------------------

exit 0
