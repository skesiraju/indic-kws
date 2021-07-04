#!/usr/bin/env bash

if [ $# -ne 1 ]; then
    echo "$0 <guj or tam or tel or mar or hin or ori>"
    exit;
fi

lang=$1

if [ "${lang}" == "tel" ]; then
    url=https://dumps.wikimedia.org/tewiki/20210601/tewiki-20210601-pages-articles-multistream.xml.bz2
elif [ "${lang}" == "tam" ]; then
    url=https://dumps.wikimedia.org/tawiki/20210601/tawiki-20210601-pages-articles-multistream.xml.bz2
elif [ "${lang}" == "guj" ]; then
    url=https://dumps.wikimedia.org/guwiki/20210601/guwiki-20210601-pages-articles-multistream.xml.bz2

elif [ "${lang}" == "hin" ]; then
    url=https://dumps.wikimedia.org/hiwiki/20210601/hiwiki-20210601-pages-articles-multistream.xml.bz2
elif [ "${lang}" == "mar" ]; then
    url=https://dumps.wikimedia.org/mrwiki/20210601/mrwiki-20210601-pages-articles-multistream.xml.bz2
elif [ "${lang}" == "ori" ]; then
    url=https://dumps.wikimedia.org/orwiki/20210601/orwiki-20210601-pages-articles-multistream.xml.bz2

else
    echo ${lang}" not understood."
    exit;
fi

mkdir -p ${lang}
cd ${lang}
wget -nc ${url}
if [ ! -d ${lang}/text ]; then
    python3 -m wikiextractor.WikiExtractor `basename $url`
fi
cd ..

if [ ! -f ${lang}/raw_data.txt ]; then
    python3 extract_docs_from_wiki_xml.py ${lang}/text/ ${lang}/out_docs/
fi


if [ ! -f ${lang}/clean_data.txt ]; then
    python3 clean_the_data.py ${lang}/raw_data.txt ${lang} ${lang}/clean_data.txt
fi
