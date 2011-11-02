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

import collections
import qlc.ngram

class WordlistStoreWithNgrams:
    
    def __init__(self, language_concept_counterpart_iterator, orthography_parser):
        self._data = collections.defaultdict(lambda : collections.defaultdict(set))
        concepts = set()
        unique_ngrams = set()
        languages = set()
        for language, concept, counterpart in language_concept_counterpart_iterator:
            languages.add(language)
            parsed_counterpart = orthography_parser.parse_string_to_graphemes(counterpart)
            ngram_tuples = set(qlc.ngram.ngrams_from_graphemes(
                parsed_counterpart
            ))

            unique_ngrams.update(ngram_tuples)
            self._data[language][concept].update(ngram_tuples)
            concepts.add(concept)

        self.concepts = list(concepts)
        self.unique_ngrams = list(unique_ngrams)
        self.languages = list(languages)
        
    def counterpart_for_language_and_concept(self, language, concept):
        return self._data[language][concept]