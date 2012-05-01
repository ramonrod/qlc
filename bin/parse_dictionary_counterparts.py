# -*- coding: utf-8 -*-

import sys
import unicodedata
from qlc.corpusreader import CorpusReaderDict
from qlc.orthography import OrthographyParser, OrthographyRulesParser

unparsables = open("unparsables.txt", "w")

def report_unparsables(wordlistdata_id, concept, counterpart, parsed_counterpart_tuple):
    invalid_parse_string = parsed_counterpart_tuple[1]
    error = wordlistdata_id+"\t"+concept+"\t"+counterpart+"\t"+invalid_parse_string
    unparsables.write(error)


if len(sys.argv) != 2:
    print("call: python parse_counterparts.py bibtex_key_source\n")

source = sys.argv[1]

# cr = CorpusReaderWordlist("data/testcorpus")
# cr = CorpusReaderWordlist("data/csv")
cr = CorpusReaderDict("data/csv")

o = OrthographyParser("data/orthography_profiles/"+source+".txt")
rules = OrthographyRulesParser("data/orthography_profiles/"+"rules_"+source+".txt")

# create a generator of corpus reader data
wordlist_iterator = ( (wordlistdata_id, head, translation)
for wordlistdata_id in cr.dictdata_ids_for_bibtex_key(source)
for head, translation in cr.heads_with_translations_for_dictdata_id(wordlistdata_id)
)

# print header
print("wordlist_id"+"\t"+"translation"+"\t"+"head"+"\t"+"graphemic_parse"+"\t"+"ipa_parse"+"\t"+"orthographic_rules_parse")

err_count = 0
errors = ""

# print all the things!
for wordlistdata_id, head, translation in wordlist_iterator:
    head = unicodedata.normalize("NFD", head)
    grapheme_parsed_counterpart_tuple = o.parse_string_to_graphemes_string(head)
    phoneme_parsed_counterpart_tuple = o.parse_string_to_ipa_string(head)
    
    if grapheme_parsed_counterpart_tuple[0] == False:
        report_unparsables(wordlistdata_id, head, translation, grapheme_parsed_counterpart_tuple)
        continue

    if phoneme_parsed_counterpart_tuple[0] == False:
        report_unparsables(wordlistdata_id, head, translation, phoneme_parsed_counterpart_tuple)
        continue
    
    grapheme_parse = grapheme_parsed_counterpart_tuple[1]
    phoneme_parse = phoneme_parsed_counterpart_tuple[1]
    rule_parsed_grapheme_parse = rules.parse_string(grapheme_parse)

    print(wordlistdata_id+"\t"+translation+"\t"+head+"\t"+grapheme_parse+"\t"+phoneme_parse+"\t"+rule_parsed_grapheme_parse)

    # check for errors in the regex rule parsing
    if not phoneme_parse == rule_parsed_grapheme_parse:
        err_count += 1
        errors += wordlistdata_id+" "
        errors += translation+"\n"
        errors += ("op: "+head+"\n")
        errors += ("pp: "+phoneme_parse+"\n")
        errors += ("gp: "+grapheme_parse+"\n")
        errors += ("rp: "+rule_parsed_grapheme_parse+"\n\n")

        """ # for further debugging
        for i in range(0, len(phoneme_parse)):
            print(ord(phoneme_parse[i]), "-", end=" ")
        print()

        for i in range(0, len(rule_parsed_grapheme_parse)):
            print(ord(rule_parsed_grapheme_parse[i]), "-", end=" ")
        print()
        """

errors += ("no match count: "+str(err_count))
print("no match count:", str(err_count), "(check std.err)\n")
print()
sys.stderr.write(errors)

