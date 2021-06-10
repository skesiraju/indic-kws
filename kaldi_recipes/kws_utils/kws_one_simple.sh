#!/bin/bash

# date: March 24, 2021
# author: Santosh Kesiraju

set -e

if [ $# -lt 7 ] || [ $# -gt 8 ]; then
    echo "Usage: $0 <language> <path_to_rttm> <path_to_ecf.xml> <keywords_file> <lang-dir> <data-dir> <decode-dir>"
    echo "  language              : tel, guj, tam, etc"
    echo "  path_to_rttm          : path to groundtruh rttm file"
    echo "  path_to_ecf           : path to ecf.xml"
    echo "  keywords_file         : path to keywords file (space separated)"
    echo "  lang-dir              : path to lang dir (data/lang) "
    echo "  data-dir              : path to data dir (data/test)"
    echo "  decode-dir            : path to decode dir (exp_new/xxx_xxx/decode_test/)"
    echo "  lw                    : Optional LM weight (default: 10)"

    echo "  Need 7 or 8 input arguments. You entered $#."
    exit;
fi

lang=$1
rttm=$2
ecf=$3
kw_file=$4

kw_name=`basename $kw_file | cut -d'.' -f1`

lang_dir=$5
data_dir=$6
decode_dir=$7
lw=${8:-10}

dir_found=0
if [ -d ${data_dir}/${lang}_${kw_name} ]; then
    echo ${data_dir}/${lang}_${kw_name}" exists. Use it or delete it."
fi

if [ -d ${decode_dir}/${lang}_${kw_name}_kws_${lw} ]; then
    echo ${decode_dir}/${lang}_${kw_name}_kws_${lw}" exists. Use it or delete it."
    dir_found=1
fi

if [ "${dir_found}" -eq "1" ]; then
    exit;
fi

cur_kw_dir=${data_dir}/${lang}_${kw_name}_kws
if [ -d ${cur_kw_dir} ]; then
    echo $cur_kw_dir" already exists. Delete it."
    exit;
fi
mkdir -p $cur_kw_dir
echo "* Created dir: "${cur_kw_dir}
cp $rttm $ecf ${cur_kw_dir}/

python3 local/create_kwslist_xml_v2.py $kw_file $lang $cur_kw_dir

sleep 1

local/kws_data_prep.sh ${lang_dir} ${data_dir} ${cur_kw_dir}

found=1
kw_res_dir=${decode_dir}/${lang}_${kw_name}_kws_${lw}
metric_file=${kw_res_dir}/metrics.txt

if [ -f $metric_file ]; then
    echo "${metric_file} already exists. Use it or delete it."

else
    local/kws_search_custom_small.sh ${lang_dir} ${data_dir} ${decode_dir} ${lw} ${lang}_${kw_name}
fi

atwv=`head -1 ${metric_file} | cut -d' ' -f3`
echo "* ATWV: ${atwv}"
sleep 1
echo "-------------------------------------------------------------------------"
