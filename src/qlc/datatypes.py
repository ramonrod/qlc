# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2011, Quantitative Language Comparison Team
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Data types of the project Quantitative Language Comparison.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import sys
import collections
import qlc.ngram

class WordlistStoreWithNgrams:
    """
    Data structure that contains language code, concepts and orthographic parsed (possible) ngram chunked strings for words. 

    Parameters
    ----------
    
    language_concept_counterpart_iterator : generator

    orthography_parser : an object that parses out graphemes

    ngram_length : length of the ngram window; default is 0

    Returns
    -------

    Nothing


    TODO:
    -----
    print matrices:
    
    0. wordlist in ngrams:
    
    lang1  concept1  word1  {#a ab bc c#}
    lang1  concept1  word2  {#i ik ka a#}
    lang2  concept1  word17 {#B Ba a#}
    lang2  concept1  word18 {#Y Yw wk k#}
    lang2  concept1  word19 ...

    x. word by word (ordered) with input from 4.
    
    """

    def __init__(self, language_concept_counterpart_iterator, orthography_parser, ngram_length=0):
        # data stored: { wordlist_id: {conept: {ngram_tuples} } }
        self._data = collections.defaultdict(lambda : collections.defaultdict(set))

        concepts = set()
        unique_ngrams = set() # using a Python set discards duplicate ngrams
        languages = set()

        for language, concept, counterpart in language_concept_counterpart_iterator:
            languages.add(language)

            # TODO:
            # updated orthography parser returns a tuple (0,1), where: 
            # 0 = True/False (whether the string correctly parsed)
            # 1 = the parsed string
            # parsed_counterpart_tuple = orthography_parser.parse_string_to_grapheme(counterpart)
            # if parsed_counterpart_tuple[0] == False:
            #    sys.stderr.write(str(parsed_counterpart_tuple))
            # parsed_counterpart = parsed_counterpart_tuple[1]

            parsed_counterpart_tuple = orthography_parser.parse_string_to_graphemes(counterpart)
            parsed_counterpart = parsed_counterpart_tuple[1]
            # print(parsed_counterpart)

            ngram_tuples = set(qlc.ngram.ngrams_from_graphemes(parsed_counterpart,2))

            unique_ngrams.update(ngram_tuples)
            self._data[language][concept].update(ngram_tuples)
            concepts.add(concept)

        self.concepts = list(concepts)
        self.unique_ngrams = list(unique_ngrams)
        self.languages = list(languages)

    def pprint(self, set):
        s = ""
        for tuple in set:
            for i in range(0, len(tuple)):
                s += tuple[i]+" "
        return s.rstrip(" ")

    def print_wordlist_in_ngrams(self):
        for language, concepts in self._data.items():
            for concept, ngrams in concepts.items():
                ngram = self.pprint(ngrams)
                print (language, "\t", concept, "\t", ngram)

    def counterpart_for_language_and_concept(self, language, concept):
        return self._data[language][concept]

    def print_matrix_concepts_by_languages(self):
        for k, v in self._data():
            print (k+"\t"+v)

    def print_concepts(self):
        print (self.concepts)
        
    def print_unique_ngrams(self):
        print (self.unique_ngrams)

    def print_languages(self):
        print (self.languages)





if __name__=="__main__":
    from qlc.CorpusReader import CorpusReaderWordlist
    from qlc.orthography import OrthographyParser

    cr = CorpusReaderWordlist("data")

    o = OrthographyParser(qlc.get_data("orthography_profiles/huber1992.txt"))

    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992')
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
    )

    w = WordlistStoreWithNgrams(wordlist_iterator, o)
    w.print_wordlist_in_ngrams()


    # to print the contents of the returned cr reader iterator:
    """
    cr = CorpusReaderWordlist("data")
    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992')
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
    )

    for wordlist_id, concept, counterpart in wordlist_iterator:
        print(wordlist_id+"\t"+concept+"\t"+counterpart)
    """
