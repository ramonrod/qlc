# -*- coding: utf-8 -*-

import sys
import qlc.orthography

"""
Example script that uses the orthography parser to parse orthographic strings into strings of graphemes given an orthography profile.

"""

def main(argv):
    if len(argv) < 4:
        print("\ncall: python ex_orthography_parser.py orthography_profile.txt data.txt transform_flag")
        print("note: if transform_flag == 1; return parse at orthography_profile column 1; if 2 then column 2, etc.\n")
        print("e.g.: python ex_orthography_parser.py thiesen1998.txt ../src/qlc/data/dictionaries/heads_with_translations_thiesen1998_25_339.txt 1")


        exit(1)

    # create a list containing the headwords from the heads file
    heads_file = open(sys.argv[2], "r")
    head_words = []

    # indicate which column of the ortography profile
    transform_flag = int(sys.argv[3])

    # put the counterparts into a list to do orthographic parse
    for line in heads_file:
        line = line.strip()
        if line.__contains__("\t"):
            tokens = line.split("\t")
            head = tokens[0]
            head_words.append(head)
        else:
            head_words.append(line)
    heads_file.close()


    # parse head words with the orthography profile and print results
    orthography_profile = sys.argv[1]

    o = qlc.orthography.OrthographyParser(orthography_profile)
    for head in head_words:
        if transform_flag == 1:
            orthography_parse = o.parse_string_to_graphemes_string(head)
        elif transform_flag == 2:
            orthography_parse = o.parse_string_to_ipa_string(head)
        else:
            raise Exception("Invalid column number!")
        print(orthography_parse)

if __name__=="__main__":
    main(sys.argv)
       
       



