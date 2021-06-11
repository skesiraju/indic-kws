#!/usr/bin/env python3

import sys
from auto_utils import load_keywords, write_kw_to_file

bad_words = [u"ஜெயலலிதா"]

if len(sys.argv) != 2:
    print("usage:", sys.argv[0], "keywords_file")
    sys.exit()

keywords = load_keywords(sys.argv[1])
print("Loaded keywords", len(keywords))

new_keywords = keywords - set(bad_words)

print("New keywords:", len(new_keywords))

write_kw_to_file(list(new_keywords), sys.argv[1])

print("Updated keywords file.")
