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
from qlc.corpusreader import CorpusReaderWordlist

import numpy
from numpy import array
numpy.set_printoptions(threshold=numpy.nan) # set so everything will print

from scipy.sparse import csr_matrix, lil_matrix, coo_matrix


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
        # write to disk the forms that can't be parsed
        unparsables = open("unparsables.txt", "w")

        ### data structures

        # data stored: { wordlist_id: {concept: {ngram_tuples} } }
        self._words = collections.defaultdict(lambda : collections.defaultdict(set))

        # data stored: {wordlist_id: {concept: [#n ng gr ra am ms s#], concept : [] }}
        self._ngrams = collections.defaultdict(lambda : collections.defaultdict(list))

        # data stored: {language: {concept: {ngram: count} } }
        self._language_counts = collections.defaultdict(lambda : collections.defaultdict(lambda : collections.defaultdict()))

        # data stored: {language: {counterpart: count} }
        self._language_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {concept: {counterpart: count} }
        self._concept_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {word: {word's-ngrams: ngram-count} }
        self._word_ngrams = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {language-specific word: {word's ngrams: ngram-count} }
        self._words_ngrams = collections.defaultdict(list)

        # data stored: {language-specific word: [word's ngrams] }
        self._language_word_ngrams = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {language: {counterpart: count} }
        self._language_specific_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        # data stored: {concept: {counterpart: count} }
        self._concept_specific_counterparts = collections.defaultdict(lambda : collections.defaultdict(int))

        ### data containers
        languages = set()
        concepts = set()
        words = set()
        parsed_words = set() # parsed words remove any identical words after ortho parsing
        unique_ngrams = set() # using a Python set discards duplicate ngrams

        non_unique_languages = set()
        non_unique_concepts = set()
        non_unique_parsed_words = set()
        non_unique_words = set()
        non_unique_parsed_words = set() 
        non_unique_ngrams = set()


        # loop over the corpus reader data and parse into data structures
        for language, concept, counterpart in language_concept_counterpart_iterator:

            # First do orthography parsing.
            parsed_counterpart_tuple = orthography_parser.parse_string_to_graphemes(counterpart) # (Unicode | ortho profile) graphemes
            # parsed_counterpart_tuple = orthography_parser.parse_string_to_ipa_phonemes(counterpart) # phonemes

            # If string is unparsable, write to file.
            if parsed_counterpart_tuple[0] == False:
                invalid_parse_string = qlc.ngram.formatted_string_from_ngrams(parsed_counterpart_tuple[1])
                unparsables.write(language+"\t"+concept+"\t"+counterpart+"\t"+invalid_parse_string+"\n")
                continue
            parsed_counterpart = parsed_counterpart_tuple[1]

            # Get ngrams as a tuple of tuples.
            ngram_tuples = qlc.ngram.ngrams_from_graphemes(parsed_counterpart,ngram_length)

            # Format that tuple of tuples into a space-delimed string.
            ngrams_string = qlc.ngram.formatted_string_from_ngrams(ngram_tuples)

            # Get the parsed version of counterparts.
            parsed_word = qlc.ngram.formatted_string_from_ngrams(parsed_counterpart)
            parsed_word = parsed_word.replace(" ", "")
            parsed_word = parsed_word.lstrip("#")
            parsed_word = parsed_word.rstrip("#")
            parsed_word = parsed_word.replace("#", " ")

            # Get set of language-specific ngrams.
            non_unique_ngram_tuples = set()
            for ngram in ngrams_string:
                non_unique_ngram_tuples.add(ngram+"_"+language)
                
            # deal with ngrams
            for ngram in ngrams_string.split():
                non_unique_ngram = ngram+"_"+language
                
                non_unique_ngrams.add(non_unique_ngram)
                self._word_ngrams[counterpart][ngram] += 1
                self._language_word_ngrams[parsed_word+"_"+language][non_unique_ngram] += 1

                # if not word in self._words_ngrams[parsed_word+"_"+language]:
                # not going to work because the word is there already for each ngram
                # wajee_7536 ['#w_7536', 'wa_7536', 'aj_7536', 'je_7536', 'ee_7536', 'e#_7536', '#w_7536', 'wa_7536', 'aj_7536', 'je_7536', 'ee_7536', 'e#_7536']

                self._words_ngrams[parsed_word+"_"+language].append(non_unique_ngram)

                if not ngram in self._language_counts[language][concept]:
                    self._language_counts[language][concept][ngram] = 1
                else:
                    self._language_counts[language][concept][ngram] += 1


            # update data structures
            self._words[language][concept].add(counterpart)
            self._ngrams[language][concept].append(ngrams_string)
            self._language_counterparts[language][counterpart] += 1
            self._concept_counterparts[concept][counterpart] += 1
            self._language_specific_counterparts[language][parsed_word+"_"+language] += 1
            self._concept_specific_counterparts[concept][parsed_word+"_"+language] += 1

            # add to header lists
            languages.add(language) # Append languages to unique set of langauge.
            concepts.add(concept)   # Append concepts to unique set of concepts.
            words.add(counterpart)  # Append words to the unique set of words.
            parsed_words.add(parsed_word) # Append the parsed counterparts.
            unique_ngrams.update(set(ngram_tuples)) # Append all the elements of ngram_tuples to unique_ngrams.
            
            # add to non-unique header lists
            non_unique_languages.add(language)
            non_unique_concepts.add(concept)
            non_unique_words.add(counterpart)
            non_unique_parsed_words.add(parsed_word+"_"+language)
            # non_unique_ngrams.update(set(ngram_tuples))

        self.non_unique_languages = list(non_unique_languages)
        self.non_unique_concepts = list(non_unique_concepts)
        self.non_unique_words = list(non_unique_words)
        self.non_unique_parsed_words = list(non_unique_parsed_words)
        self.non_unique_ngrams = list(non_unique_ngrams)

        self.non_unique_languages.sort()
        self.non_unique_concepts.sort()
        self.non_unique_words.sort()
        self.non_unique_parsed_words.sort()
        self.non_unique_ngrams.sort()

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
            # print(self.words[i])
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

    # words/counterparts (rows) x graphemes (cols) x index (= if counterpart appears in that language
    def non_unique_words_graphemes_counts_matrix(self):
        # WG = numpy.empty( (len(self.non_unique_parsed_words),len(self.non_unique_ngrams)), dtype=int )
        WG = lil_matrix( (len(self.non_unique_parsed_words),len(self.non_unique_ngrams)), dtype=int)
        for i in range(0, len(self.non_unique_parsed_words)):
            for j in range(0, len(self.non_unique_ngrams)):
                # WG[i][j] = 0
                # check to see if the word has the ngram
                ngrams = self._language_word_ngrams[self.non_unique_parsed_words[i]][self.non_unique_ngrams[j]]
                if ngrams != 0:
                    WG[i,j] = 1
        return WG


    def non_unique_words_graphemes_counts_matrix2(self):
        # WG = numpy.empty( (len(self.non_unique_parsed_words),len(self.non_unique_ngrams)), dtype=int )
        row = []
        col = []
        data = []
        for i in range(0, len(self.non_unique_parsed_words)):
            for j in range(0, len(self.non_unique_ngrams)):
                ngrams = self._language_word_ngrams[self.non_unique_parsed_words[i]][self.non_unique_ngrams[j]]
                if ngrams != 0:
                    row.append(i)
                    col.append(j)
                    data.append(1)
        row = array(row)
        col = array(col)
        data = array(data)
        WG = coo_matrix((data,(row,col)), shape=(len(self.non_unique_parsed_words),len(self.non_unique_ngrams)), dtype=int)
        return WG



    # words/counterparts (rows) x languages (cols) x index (= if counterpart appears in that language)
    def non_unique_words_languages_counts_matrix(self):
        WL = numpy.empty( (len(self.non_unique_parsed_words),len(self.languages)), dtype=int )
        for i in range(0, len(self.non_unique_parsed_words)):
            for j in range(0, len(self.languages)):
                WL[i][j] = 0
                words = self._language_specific_counterparts[self.languages[j]][self.non_unique_parsed_words[i]]
                if words != 0:
                    WL[i][j] = 1

        return WL

    # words/counterparts (rows) x concepts (cols) x index (= if counterpart appears in that language)
    def non_unique_words_concepts_counts_matrix(self):
        WM = numpy.empty( (len(self.non_unique_parsed_words),len(self.concepts)), dtype=int )
        for i in range(0, len(self.non_unique_parsed_words)):
            for j in range(0, len(self.concepts)):
                WM[i][j] = 0
                words = self._concept_specific_counterparts[self.concepts[j]][self.non_unique_parsed_words[i]]
                if words != 0:
                    WM[i][j] = 1
        return WM

    def get_gp_matrix(self):
        WP = numpy.empty( (len(self.non_unique_ngrams),len(self.unique_ngrams)), dtype=int )
        for i in range(0, len(self.non_unique_ngrams)):
            for j in range(0, len(self.unique_ngrams)):
                WP[i][j] = 0
                tokens = self.non_unique_ngrams[i].partition("_")
                g = tokens[0] # get the grapheme-ngram without language

                # get the phoneme-ngram; recompose from tuples
                p = "" 
                for ngram in self.unique_ngrams[j]:
                    p += ngram

                if g == p:
                    WP[i][j] = 1
        return WP

    def get_ngrams_indices(self):
        for gram in self.non_unique_ngrams:
            print(gram+"\t"+str(self.non_unique_ngrams.index(gram)))

    def get_words_ngrams_strings(self):
        self._get_words_ngrams(False)

    def get_words_ngrams_indices(self):
        self._get_words_ngrams(True)

    def _get_words_ngrams(self, index):
        for word in self.non_unique_parsed_words:
            if not word in self._words_ngrams:
                print("warning: non_unique_parsed words does not match _words.ngrams")
                sys.exit(1)
            result = word
            for gram in self._words_ngrams[word]:
                if index:
                    gram = str(self.non_unique_ngrams.index(gram))
                result += "\t"+gram
            print(result)

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
        for language, concepts in self._words.items():
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

    def write_header(self, list, source, ext):
        file = open(source+"/"+source+ext, "w")
        count = 0
        for item in list:
            count += 1
            file.write(str(count)+"\t"+item)
        file.close()

    def make_ngram_header(self):
        count = 0
        for i in range(0, len(w.unique_ngrams)):
            count += 1
            composed_ngram = ""
            for ngram in w.unique_ngrams[i]:
                composed_ngram += ngram
            print(str(count)+"\t"+composed_ngram)

    def write_wordlistid_languagename(self, source): 
        file = open(source+"/"+source+"_wordlistids_lgnames_header.txt", "w")
        wordlist_ids = []
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key(source):
            wordlist_ids.append(wordlistdata_id)
        wordlist_ids.sort()
        for wordlist_id in wordlist_ids:
            file.write(wordlist_id+"\t"+cr.get_language_bookname_for_wordlistdata_id(wordlist_id)+"\n")
        file.close()


if __name__=="__main__":
    import sys
    from qlc.corpusreader import CorpusReaderWordlist
    from qlc.orthography import OrthographyParser, GraphemeParser
    from scipy.io import mmread, mmwrite # write sparse matrices

    if len(sys.argv) != 2:
        print("call: python matrix.py source\n")
        print("python matrix.py huber1992\n")

    source = sys.argv[1] # dictionary/wordlist source key
    output_dir = "zgraggen1980/"

    # get data from corpus reader
    # cr = CorpusReaderWordlist("data/csv")      # real data
    cr = CorpusReaderWordlist("data/testcorpus") # test data
    
    # initialize orthography parser for source

    # o = OrthographyParser(qlc.get_data("orthography_profiles/"+source+".txt"))
    o = GraphemeParser()

    # create generator of corpus reader data
    wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
        for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key(source)
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
    )

    # print all the things!
    """
    for wordlistdata_id, concept, counterpart in wordlist_iterator:
        print(wordlistdata_id+"\t"+concept+"\t"+counterpart)
    sys.exit(1)
    """


    # initialize matrix class
    w = WordlistStoreWithNgrams(wordlist_iterator, o, 2) # pass ortho parser and ngram length

    # Create parsed and language-specific word matrices and 
    # convert to sparse matrix (csr format best for matrix multiplication)

    # WL = w.non_unique_words_languages_counts_matrix()
    # WL_sparse = csr_matrix(WL)
    # mmwrite(output_dir+source+"_WL.mtx", WL_sparse)

    # WM = w.non_unique_words_concepts_counts_matrix()
    # WM_sparse = csr_matrix(WM)
    # mmwrite(output_dir+source+"_WM2.mtx", WM_sparse)

    # WG = w.non_unique_words_graphemes_counts_matrix()
    WG = w.non_unique_words_graphemes_counts_matrix2()
    # WG_sparse = csr_matrix(WG)
    mmwrite("WG.mtx", WG)

    # mmwrite(output_dir+source+"_WG.mtx", WG)

    # WP = w.get_gp_matrix()
    # WP_sparse = csr_matrix(WP) 
    # mmwrite(output_dir+source+"_WP.mtx", WP_sparse)

    # write headers (non-unique)
    # w.write_wordlistid_languagename(source)
    # w.write_header(w.non_unique_parsed_words, source, "_words_header.txt")
    # w.write_header(w.concepts, source, "_meanings_header.txt")
    # w.write_header(w.non_unique_ngrams, source, "_ngrams_header.txt")
    
    # print the word and ngrams/ngrams-indices
    # w.get_words_ngrams_strings()    
    # w.get_words_ngrams_indices()
    # w.get_ngrams_indices()
    # w.make_ngram_header() # make phoneme header


    # w.make_header(w.non_unique_parsed_words)
    # w.make_header(w.concepts)
    # w.make_header(w.non_unique_ngrams)


    # anene_7522 #a_7522 an_7522 ne_7522 en_7522 ne_7522 e#_7522
    # w.get_words_ngrams_strings()




    ### depreciated

    # Create ***unique*** word matrix (currently depreciated)
    # WL = w.words_languages_counts_matrix()
    # WM = w.words_concepts_counts_matrix()
    # WG = w.words_graphemes_counts_matrix()

    # write headers (unique -- depreciated)
    # w.make_header(w.parsed_words)
    # w.make_ngram_header()
    # w.make_header(w.languages)








    
    # TODO -- write method to look up two words for Needleman-Wunsch comparison

    
