#!/usr/bin/env bash

if [ $# -le 4 ]; then
    echo "usage: $0 <lang> <cat_name> <decode_dir> <out_res_file> [lmwt: default=10]"
    exit;
fi

lang=$1
cat_name=$2
decode_dir=$3
out_f=$4
lmwt=${5:-10}

echo ${cat_name} "ATWV" > ${out_f}
for i in {1..25}; do
    metric_file=${decode_dir}/${lang}_${cat_name}_${i}_kws_${lmwt}/metrics.txt
    if [ -f ${metric_file} ]; then
        echo ${i} `head -1 $metric_file | cut -d'=' -f2`
    fi
done >> ${out_f}
cat ${out_f}
