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

    """

    def __init__(self, language_concept_counterpart_iterator, orthography_parser, ngram_length):
        # data stored: { wordlist_id: {conept: {ngram_tuples} } }
        self._words = collections.defaultdict(lambda : collections.defaultdict(set))
        self._ngrams = collections.defaultdict(lambda : collections.defaultdict(list))

        languages = set()
        concepts = set()
        unique_ngrams = set() # using a Python set discards duplicate ngrams

        for language, concept, counterpart in language_concept_counterpart_iterator:
            parsed_counterpart_tuple = orthography_parser.parse_string_to_graphemes(counterpart)
            parsed_counterpart = parsed_counterpart_tuple[1]
            # Get ngrams as a tuple of tuples.
            ngram_tuples = qlc.ngram.ngrams_from_graphemes(parsed_counterpart,ngram_length)
            # Format that tuple of tuples into a space-delimed string.
            ngrams_string = qlc.ngram.formatted_string_from_ngrams(ngram_tuples)

            self._words[language][concept].add(counterpart)
            self._ngrams[language][concept].append(ngrams_string)

            # Append language string to unique set of langauge.
            languages.add(language)
            # Append concept string to unique set of concepts.
            concepts.add(concept)
            # Add all the elements of ngram_tuples to unique_ngrams.
            unique_ngrams.update(set(ngram_tuples))

        self.concepts = list(concepts)
        self.unique_ngrams = list(unique_ngrams)
        self.languages = list(languages)
        self.concepts.sort()
        self.unique_ngrams.sort()
        self.languages.sort()

    def print_concept_words_by_languages(self):
        # print header
        print("language", end="")
        for concept in self.concepts:
            print("\t"+concept, end="")
        print()
        for language in self.languages:
            print(language, end="")
            for concept in self.concepts:
                words = self._words[language][concept]
                print("\t"+",".join(words), end="")
            print()


    def print_concept_ngrams_by_languages(self):
        # print header
        print("language", end="")
        for concept in self.concepts:
            print("\t"+concept, end="")
        print()
        for language in self.languages:
            print(language, end="")
            for concept in self.concepts:
                # ngrams is a list of strings (formatted ngram strings)
                ngrams = self._ngrams[language][concept]
                print("\t"+" ".join(ngrams), end="")
            print()

    def print_wordlist_in_ngrams(self):
        for language, concepts in self._data.items():
            for concept, ngrams in concepts.items():
                ngram = ""
                for gram in ngrams:
                    ngram += "".join(gram)+" "
                    ngram = ngram.rstrip(" ")                
                print (language, "\t", concept, "\t", ngram)

    def pprint(self, set):
        s = ""
        for tuple in set:
            for i in range(0, len(tuple)):
                s += tuple[i]+" "
        return s.rstrip(" ")



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

    cr = CorpusReaderWordlist("data/csv")

    o = OrthographyParser(qlc.get_data("orthography_profiles/huber1992.txt"))

    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992')
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
    )

    w = WordlistStoreWithNgrams(wordlist_iterator, o, 2)
#    w.print_concept_words_by_languages()
    w.print_concept_ngrams_by_languages()

    # w.print_wordlist_in_ngrams()


