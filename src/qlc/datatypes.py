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
import numpy
numpy.set_printoptions(threshold=numpy.nan) # set so everything will print

import scipy.sparse as sps
from scipy.sparse import csr_matrix

class WordlistStoreWithNgrams:
    """
    Data structure that contains language code, concepts and orthographic parsed (possible) ngram chunked strings for words. 

    I try to give method names by rows x columns, e.g. print_concepts_languages_ngrams prints a 2D matrix of 
    concepts (in rows) by languages (columns) by ngrams (in each cell).

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

        # data stored: {language: {concept: {ngram: count} } }
        self._language_counts = collections.defaultdict(lambda : collections.defaultdict(lambda : collections.defaultdict()))

        # data stored: {language: {counterpart: count} }
        self._language_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {concept: {counterpart: count} }
        self._concept_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {word: {word's-ngrams: ngram-count} }
        self._word_ngrams = collections.defaultdict(lambda : collections.defaultdict(int))


        languages = set()
        concepts = set()
        words = set()
        parsed_words = set()
        unique_ngrams = set() # using a Python set discards duplicate ngrams


        for language, concept, counterpart in language_concept_counterpart_iterator:
            # Do orthography parsing
            # here i have two lines; first to parse column 1 of ortho profile; second to parse line 2 (IPA)
            # parsed_counterpart_tuple = orthography_parser.parse_string_to_graphemes(counterpart)
            parsed_counterpart_tuple = orthography_parser.parse_string_to_ipa_phonemes(counterpart)

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
            self._language_counterparts[language][counterpart] += 1
            self._concept_counterparts[concept][counterpart] += 1


            # deal with ngrams
            for ngram in ngrams_string.split():
                self._word_ngrams[counterpart][ngram] += 1

                if not ngram in self._language_counts[language][concept]:
                    self._language_counts[language][concept][ngram] = 1
                else:
                    self._language_counts[language][concept][ngram] += 1

            # to get the parsed version of counterparts for 
            parsed_word = qlc.ngram.formatted_string_from_ngrams(parsed_counterpart)
            parsed_word = parsed_word.replace(" ", "")
            parsed_word = parsed_word.lstrip("#")
            parsed_word = parsed_word.rstrip("#")
            parsed_word = parsed_word.replace("#", " ")

            languages.add(language) # Append language string to unique set of langauge.
            concepts.add(concept)   # Append language string to unique set of langauge.
            words.add(counterpart)  # Append all words to the unique set of words.
            parsed_words.add(parsed_word) # Append the parsed counterparts.
            unique_ngrams.update(set(ngram_tuples)) # Append all the elements of ngram_tuples to unique_ngrams.


        self.languages = list(languages)
        self.concepts = list(concepts)
        self.words = list(words)
        self.parsed_words = list(parsed_words)
        self.unique_ngrams = list(unique_ngrams)

        self.languages.sort()
        self.concepts.sort()
        self.words.sort()
        self.parsed_words.sort()
        self.unique_ngrams.sort()

        

        """
        for language, concept in self._language_counts.items():
            if language == "7509":
                for concept, ngrams in self._language_counts[language].items():
                    print (language, concept, ngrams)

        sys.exit()
        """

    def get_length_longest_set_word(self):
        """
        Return the length of the longest set of combined word (by Unicode characters)
        for a given concept in a given language in the dataset.
        """
        length = 0
        longest_set_words = ""
        for concept in self.concepts:
            for language in self.languages:
                words = self._words[language][concept]
                joined_words = ",".join(words)
                if len(joined_words) > length:
                    length = len(joined_words)
                    longest_set_words = joined_words
        return length
                    

    def concepts_languages_counts_matrix(self):
        # create numpy array with data type int to hold # of words x languages in a (sparse) matrix
        # create an empty numpy 2D array with length (rows) of words
        # and length (cols) of languages; set datatype to int 

        WL = numpy.empty( (len(self.words),len(self.languages)), dtype=int )

        for i in range(0, len(self.concepts)):
            for j in range(0, len(self.languages)):
                WL[i][j] = 0
                words = self._words[self.languages[j]][self.concepts[i]]
                if len(words) != 0:
                    WL[i][j] = 1
        return CL


    # words/counterparts (rows) x languages (cols) x index (= if counterpart appears in that language)
    def words_languages_counts_matrix(self):
        # create numpy array with data type int to hold words x meanings (concepts) x 0/1
        # create an empty numpy 2D array with length (rows) of words
        # and length (cols) of languages; set datatype to int 

        WL = numpy.empty( (len(self.words),len(self.languages)), dtype=int )

        for i in range(0, len(self.words)):
            for j in range(0, len(self.languages)):
                WL[i][j] = 0
                words = self._language_counterparts[self.languages[j]][self.words[i]]
                if words != 0:
                    WL[i][j] = 1

        return WL

    # words/counterparts (rows) x concepts (cols) x index (= if counterpart appears in that language)
    def words_concepts_counts_matrix(self):
        WM = numpy.empty( (len(self.words),len(self.concepts)), dtype=int )

        for i in range(0, len(self.words)):
            for j in range(0, len(self.concepts)):
                WM[i][j] = 0
                words = self._concept_counterparts[self.concepts[j]][self.words[i]]
                if words != 0:
                    WM[i][j] = 1
        return WM

    # words/counterparts (rows) x graphemes (cols) x index (= if counterpart appears in that language)
    def words_graphemes_counts_matrix(self):
        WG = numpy.empty( (len(self.words),len(self.unique_ngrams)), dtype=int )
        for i in range(0, len(self.words)):
            for j in range(0, len(self.unique_ngrams)):
                WG[i][j] = 0

                # stupid hack to recompose the ngram -- yay i'm glad we used tuples
                composed_ngram = ""
                for ngram in self.unique_ngrams[j]:
                    composed_ngram += ngram

                # check to see if the word has the ngram
                ngrams = self._word_ngrams[self.words[i]][composed_ngram]

                if ngrams != 0:
                    WG[i][j] = 1
        return WG


    def concepts_languages_words_matrix(self):
        # create numpy array with data type str to hold meanings x languages in a matrix
        max_word_length = self.get_length_longest_set_word()

        # create an empty numpy 2D array with length (rows) of concepts
        # and length (cols) of languages; set datatype to Unicode, the length of each cell
        # is the maximum word length

        CL = numpy.empty( (len(self.concepts),len(self.languages)), dtype="U"+str(max_word_length) )

        for i in range(0, len(self.concepts)):
            for j in range(0, len(self.languages)):
                cell_data = ""
                words = self._words[self.languages[j]][self.concepts[i]]
                if len(words) != 0:
                    cell_data = ",".join(words)
                CL[i][j] = cell_data

        for row in range(0, len(CL)):
            for col in range(0, len(CL[0])):
                print(CL[row][col]+"\t", end="")
            print()




    def print_concepts_languages_ngrams(self):
        """
        Prints a 2D matrix of concepts (rows) by languages (cols) by ngrams (in cells).
        """
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

    def print_concepts_languages_words(self):
        """
        Prints a 2D matrix of concepts (rows) by languages (cols) by ngrams (in cells).
        """
        print ("CxL", end="")
        for language in self.languages:
            print ("\t"+language, end="")
        print()
        for concept in self.concepts:
            print(concept, end="")
            for language in self.languages:
                words = self._words[language][concept]
                print("\t"+",".join(words), end="")
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

    def print_languages_concepts_words(self):
        """
        Print a 2D matrix of languages (rows) by concepts (cols) by words (in cells).
        """
        # print header
        print("LANGUAGE", end="")
        for concept in self.concepts:
            print("\t"+concept, end="")
        print()
        for language in self.languages:
            print(language, end="")
            for concept in self.concepts:
                words = self._words[language][concept]
                print("\t"+",".join(words), end="")
            print()


    def print_languages_concepts_ngrams(self):
        """
        Print 2D matrix of languages (rows) by concepts (cols) by ngrams (in cells).
        """
        # print header
        print("LANGUAGE", end="")
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
        """
        Prints a dump of a word list with ngrams, e.g.:

        LANG1 \t CONCEPT1 \t WORD1 \t #n ng gr ra am ms s#
        LANG1 \t CONCEPT1 \t WORD2 \t #gr ra am ms s#
        ...

        """
        for language, concepts in self._data.items():
            for concept, ngrams in concepts.items():
                ngram = ""
                for gram in ngrams:
                    ngram += "".join(gram)+" "
                    ngram = ngram.rstrip(" ")                
                print (language, "\t", concept, "\t", ngram)


    def make_header(self, list):
        count = 0
        for item in list:
            count += 1
            print(str(count)+"\t"+item)

    def make_ngram_header(self):
        count = 0
        for i in range(0, len(w.unique_ngrams)):
            count += 1
            composed_ngram = ""
            for ngram in w.unique_ngrams[i]:
                composed_ngram += ngram
            print(str(count)+"\t"+composed_ngram)




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
    from qlc.corpusreader import CorpusReaderWordlist
    from qlc.orthography import OrthographyParser
    from scipy.io import mmread, mmwrite # write sparse matrices

    # cr = CorpusReaderWordlist("data/csv") # "data/testcorpus" -- for test corpus
    cr = CorpusReaderWordlist("data/testcorpus")

    o = OrthographyParser(qlc.get_data("orthography_profiles/huber1992.txt"))

    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992')
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
    )

    w = WordlistStoreWithNgrams(wordlist_iterator, o, 2) # pass ortho parser and ngram length

    # uncomment (one) to create matrix
    # WL = w.words_languages_counts_matrix()
    # WM = w.words_concepts_counts_matrix()
    # WG = w.words_graphemes_counts_matrix()

    # uncomment correspondning line (from above) to make sparse matrix
    # WL_sparse = csr_matrix(WL)
    # WM_sparse = csr_matrix(WM)
    # WG_sparse = csr_matrix(WG)

    # uncomment corresponding line (from above) to write sparse matrix to disk
    # mmwrite('2_sparse_matrices/test_huber1992_WL.mtx', WL_sparse)
    # mmwrite('2_sparse_matrices/test_huber1992_WM.mtx', WM_sparse)
    # mmwrite('2_sparse_matrices/test_huber1992_WG.mtx', WG_sparse)

    # uncomment (one) to make headers
    w.make_header(w.parsed_words)
    # w.make_header(w.concepts)
    # w.make_ngram_header()


    # uncomment to get the length of the unique ngrams
    # print(len(w.unique_ngrams))

