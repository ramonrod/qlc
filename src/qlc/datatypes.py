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
        unparsables = open("unparsables.txt", "w")

        # data stored: { wordlist_id: {concept: {ngram_tuples} } }
        self._words = collections.defaultdict(lambda : collections.defaultdict(set))
        self._ngrams = collections.defaultdict(lambda : collections.defaultdict(list))
        # {language: {concept: {ngram: count} } }
        self._language_counts = collections.defaultdict(lambda : collections.defaultdict(lambda : collections.defaultdict()))
                                                        
        languages = set()
        concepts = set()
        unique_ngrams = set() # using a Python set discards duplicate ngrams

        for language, concept, counterpart in language_concept_counterpart_iterator:
            # Do orthography parsing
            parsed_counterpart_tuple = orthography_parser.parse_string_to_graphemes(counterpart)
            # If unparsable, write to file.
            if parsed_counterpart_tuple[0] == False:
                invalid_parse_string = qlc.ngram.formatted_string_from_ngrams(parsed_counterpart_tuple[1])
                unparsables.write(language+"\t"+concept+"\t"+counterpart+"\t"+invalid_parse_string+"\n")
                continue
            parsed_counterpart = parsed_counterpart_tuple[1]

            # Get ngrams as a tuple of tuples.
            ngram_tuples = qlc.ngram.ngrams_from_graphemes(parsed_counterpart,ngram_length)

            # Format that tuple of tuples into a space-delimed string.
            ngrams_string = qlc.ngram.formatted_string_from_ngrams(ngram_tuples)

            self._words[language][concept].add(counterpart)
            self._ngrams[language][concept].append(ngrams_string)

            for ngram in ngrams_string.split():
                if not ngram in self._language_counts[language][concept]:
                    self._language_counts[language][concept][ngram] = 1
                else:
                    self._language_counts[language][concept][ngram] += 1

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

        """
        for language, concept in self._language_counts.items():
            if language == "7509":
                for concept, ngrams in self._language_counts[language].items():
                    print (language, concept, ngrams)

        sys.exit()
        """

    def print_languages_concepts_ngrams(self):
        print ("CONCEPTS", end="")
        for language in self.languages:
            print ("\t"+language, end="")
        print()
        for concept in self.concepts:
            print(concept, end="")
            for language in self.languages:
                ngrams = self._ngrams[language][concept]
                print("\t"+" ".join(ngrams), end="")
            print()

    def print_ngrams_concepts_ngramcounts(self, language):
        # print header
        print(language, end="")
        for ngram in self.unique_ngrams:
            ngram_string = qlc.ngram.formatted_string_from_ngrams(ngram)
            ngram_string = ngram_string.replace(" ", "")
            print("\t"+ngram_string, end="")
        print()

        # print rows
        counts = self._language_counts[language]
        for concept in self.concepts:
            print(concept, end="")
            for ngram in self.unique_ngrams:
                result = ""
                ngram_string = qlc.ngram.formatted_string_from_ngrams(ngram)
                ngram_string = ngram_string.replace(" ", "")                
                if not ngram_string in counts[concept]:
                    result = "NA"
                else:
                    result = str(counts[concept][ngram_string])
                print("\t"+result, end="")
            print()


    def print_concepts_languages_words(self):
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


    def print_concepts_languages_ngrams(self):
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

    # maybe move the wordlist in ngrams function here from matrix.py
    def print_wordlist_in_ngrams(self):
        for language, concepts in self._data.items():
            for concept, ngrams in concepts.items():
                ngram = ""
                for gram in ngrams:
                    ngram += "".join(gram)+" "
                    ngram = ngram.rstrip(" ")                
                print (language, "\t", concept, "\t", ngram)


    # probably don't need these

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
    # w.print_concepts_languages_words()
    # w.print_concepts_languages_ngrams()
    # w.print_ngrams_concepts_ngramcounts("7509")

    # print a ngram by concept by ngram count matrix for all language
    # maybe put this in a method to call all
    """
    languages = cr.wordlistdata_ids_for_bibtex_key('huber1992')
    for language in languages:
        w.print_ngrams_concepts_ngramcounts(language)
        print()
        print()
        """

    # w.print_languages_concepts_ngrams()
