#!/bin/bash

# date: March 24, 2021
# author: Santosh Kesiraju

set -e

if [ $# -ne 10 ]; then
    echo "Usage: $0 <language> <path_to_rttm> <path_to_ecf.xml> <dir_path_to_wlen/> <dir_path_to_wfreq/> <dir_path_to_conf_dist/> <lang-dir> <data-dir> <decode-dir> <results-dir>"
    echo "  language              : tel, guj, tam, etc"
    echo "  path_to_rttm          : path to groundtruh rttm file"
    echo "  path_to_ecf           : path to ecf.xml"
    echo "  dir_path_to_wlen      : directory containing ONLY keywords (.txt) organized by word length"
    echo "  dir_path_to_wfreq     : directory containing ONLY keywords (.txt) organized by word frequency"
    echo "  dir_path_to_conf_dist : directory containing ONLY keywords (.txt) organized by avg confusability distance"
    echo "  lang-dir              : path to lang dir (data/lang) "
    echo "  data-dir              : path to data dir (data/test)"
    echo "  decode-dir            : path to decode dir (exp_new/xxx_xxx/decode_test/)"
    echo "  results-dir           : dir path to save the ATWV best scores for wlen, wfreq, conf_dist"
    exit ;
fi

lang=$1
rttm=`realpath $2`
ecf=`realpath $3`
wlen_dir=`realpath $4`
wfreq_dir=`realpath $5`
conf_dir=`realpath $6`

lang_dir=$7
data_dir=`realpath $8`
decode_dir=`realpath $9`
mkdir -p ${10}
res_dir=`realpath ${10}`

for sub_d in ${wlen_dir} ${wfreq_dir} ${conf_dir}; do

    echo "Processing keywords from: "${sub_d}
    param=`basename ${sub_d}`

    res_file=${res_dir}/${lang}_${param}_atwv_results.txt
    if [ -f ${res_file} ]; then
	    echo "${res_file} already exists. Check it. If not required, rename/delete it and run again."

    else

        echo "# ${param} ATWV" > ${res_file}

        for f in `find ${sub_d}/ -name "*.txt"`; do

	        base=`basename $f | cut -d'.' -f1`
	        echo $base

	        cur_kw_dir=${data_dir}/${lang}_${base}_kws
	        mkdir -p $cur_kw_dir
	        cp $rttm $ecf ${cur_kw_dir}/

	        python3 local/create_kwslist_xml_v2.py $f $lang $cur_kw_dir

	        local/kws_data_prep.sh ${lang_dir} ${data_dir} ${cur_kw_dir}

	        found=1
	        for lw in {7..17}; do
	            kw_res_dir=${decode_dir}/${lang}_${base}_kws_${lw}
	            metric_file=${kw_res_dir}/metrics.txt

	            if [ ! -f $metric_file ]; then
		            found=0
		            break;
	            fi
	        done
	        if [ "${found}" = "0" ]; then
	            local/kws_search_custom.sh ${lang_dir} ${data_dir} ${decode_dir} ${lang}_${base}
	        else
	            echo "* INFO KWS results (${lang}_${base}_kws_*) are already present in ${decode_dir}. \
                If you would like to  redo the search, delete older kws search directories and try again."
	        fi

	        best_atwv=`for lw in {7..17}; do echo "\`head -1 ${decode_dir}/${lang}_${base}_kws_${lw}/metrics.txt | cut -d' ' -f3\`" ; done | sort  | tail -1`
	        val=`echo ${base} | awk -F"_" '{print $NF}'`
	        echo ${val}" "${best_atwv} >> ${res_file}

        done

        if [ -f sort_results_file.py ]; then
            python3 sort_results_file.py ${res_file}
        fi
    fi

done

echo "* Results saved in ${res_dir}"
