#!/usr/bin/env python3

import os
import argparse
import sys


def main_func(args):

    os.makedirs(args.out_dir, exist_ok=True)

    kw_list_file = os.path.join(args.out_dir, "kwlist.xml")
    if os.path.exists(kw_list_file):
        print(kw_list_file, 'already exists. Will overwrite it.')

    f=open(args.keywords_file)
    lines = f.readlines()
    f.close()
    print(len(lines), "keywords have been read from", args.keywords_file)
    # print("corresponding kwlist.xml file will be generated")
    # print("================================================")
    # l=input("Enter the language that you are working on: ")
    # print("Generating kwlist.xml file")
    g=open(kw_list_file, "w", encoding="utf-8")
    g.write('<kwlist ecf_filename="ecf.xml" language="'+args.lang+'" encoding="UTF-8" compareNormalize="" version="Example keywords">\n')

    for line in lines:
        temp = line.strip().split(" ")
        if len(temp) != 2:
            print(args.keywords_file, "should only contain two columns in the format: <num> <word>.",
                  file=sys.stderr)
            g.close()
            sys.exit()

        st = u''
        for j in temp[1:]:
            st += j+" "
        s='  <kw kwid="'+temp[0]+'">\n'+\
    '    <kwtext>'+st.strip()+'</kwtext>\n'+\
    '  </kw>\n'
        g.write(s)
    g.write('</kwlist>\n')
    g.close()
    print("success: kwlist.xml saved in", args.out_dir)


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("keywords_file", help="path to keywords.txt file")
    parser.add_argument("lang", help="language")
    parser.add_argument("out_dir", help="dir path where kwlist.xml should be saved.")
    args = parser.parse_args()

    main_func(args)
