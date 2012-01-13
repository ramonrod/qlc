# -*- coding: utf-8 -*-

import sys
from qlc.CorpusReader import CorpusReaderWordlist
import qlc.ngram
import qlc.orthography

"""
Script to print a wordlist in ngrams based using the CorpusReaderWordlist class

"""

def print_wordlist_in_ngrams(data_path, bibtex_key, orthography_parser, ngram_length):
    invalid_parses = []
    cr = CorpusReaderWordlist(data_path)
    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
                          for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key(bibtex_key)
                          for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
                          )
                          
    for wordlist_id, concept, counterpart in wordlist_iterator:
        ngram = ""
        parsed_counterpart = orthography_parser.parse_string_to_graphemes_string(counterpart)

        if parsed_counterpart[0] == False:
            invalid_parses.append(parsed_counterpart[1])

        else:
            ngram_parse = qlc.ngram.ngrams_from_graphemes(tuple(parsed_counterpart[1].split()), ngram_length)
            
            for element in ngram_parse:
                ngram += "".join(element)+" "
            ngram = ngram.rstrip(" ")

        print(wordlist_id+"\t"+concept+"\t"+ngram)

    print()
    print("INVALID PARSES:")
    for parse in invalid_parses:
        print(parse)


if __name__=="__main__":
    o = qlc.orthography.OrthographyParser(qlc.get_data("orthography_profiles/huber1992.txt"))
    print_wordlist_in_ngrams("data/csv", "huber1992", o, 2)

