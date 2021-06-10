#!/bin/bash

# date: March 24, 2021
# author: Santosh Kesiraju

set -e

if [ $# -ne 9 ]; then
    echo "Usage: $0 <language> <unique_name> <path_to_rttm> <path_to_ecf.xml> <keywords_file> <lang-dir> <data-dir> <decode-dir> <results-dir>"
    echo "  language              : tel, guj, tam, etc"
    echo "  unique_name           : unique name for the current kw experiment"
    echo "  path_to_rttm          : path to groundtruh rttm file"
    echo "  path_to_ecf           : path to ecf.xml"
    echo "  keywords_file         : path to keywords file (space separated)"
    echo "  lang-dir              : path to lang dir (data/lang) "
    echo "  data-dir              : path to data dir (data/test)"
    echo "  decode-dir            : path to decode dir (exp_new/xxx_xxx/decode_test/)"
    echo "  results-dir           : dir path to save the ATWV best score"
    exit ;
fi


lang=$1
kw_name=$2
rttm=`realpath $3`
ecf=`realpath $4`
kw_file=`realpath $5`

lang_dir=$6
data_dir=`realpath $7`
decode_dir=`realpath $8`
mkdir -p ${9}
res_dir=`realpath ${9}`


res_file=${res_dir}/${lang}_atwv_results.txt
if [ -f ${res_file} ]; then
	echo "${res_file} already exists. Check it. If not required, rename/delete it and run again."
	exit;
fi

cur_kw_dir=${data_dir}/${lang}_${kw_name}_kws
if [ -d ${cur_kw_dir} ]; then
    echo $cur_kw_dir" already exists. Deleting it"
    rm -rf ${cur_kw_dir}
    # exit;
fi
mkdir -p $cur_kw_dir
echo "* Created dir: "${cur_kw_dir}
cp $rttm $ecf ${cur_kw_dir}/

python3 local/create_kwslist_xml_v2.py $kw_file $lang $cur_kw_dir

local/kws_data_prep.sh ${lang_dir} ${data_dir} ${cur_kw_dir}

found=1
for lw in {7..17}; do
	kw_res_dir=${decode_dir}/${lang}_kws_${lw}
	metric_file=${kw_res_dir}/metrics.txt

	if [ ! -f $metric_file ]; then
		found=0
		break;
	fi
done
if [ "${found}" = "0" ]; then
    local/kws_search_custom.sh ${lang_dir} ${data_dir} ${decode_dir} ${lang}_${kw_name}
else
    echo "* INFO KWS results (${lang}_kws_*) are already present in ${decode_dir}. \
If you would like to  redo the search, delete older kws search directories and try again."
fi

best_atwv=`for lw in {7..17}; do echo "\`head -1 ${decode_dir}/${lang}_${kw_name}_kws_${lw}/metrics.txt | cut -d' ' -f3\` ${lw}" ; done | sort  | tail -1`
#val=`echo ${base} | awk -F"_" '{print $NF}'`
echo ${best_atwv} >> ${res_file}






echo "`cat ${res_file}`"" - best ATWV (consider this ONLY for dev data. for test data note down the LM weight, and check the metrics.txt from appropriate directory)"
echo "* Results saved in ${res_dir}"
