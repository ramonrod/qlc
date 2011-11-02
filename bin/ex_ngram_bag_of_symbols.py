# encoding: utf-8
#!/usr/bin/env python3

"""
Documentation.

Authors:

* The Team
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2011
#  The Quantitative Language Comparison (scikits.qlc) Team
#
#  Distributed under the terms of the BSD License.
#
#  The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys, os, itertools, collections

from qlc.CorpusReader import CorpusReaderWordlist
from qlc.orthography import OrthographyParser

import qlc.ngram
import numpy

def main(argv):

    if len(argv) < 2:
        print("call: counterparts_huber1992.py data_path")
        exit(1)

    cr = CorpusReaderWordlist(argv[1])
    o = orthography(os.path.join(argv[1], "orthography_profiles", "huber1992.txt"))
    
    ngrams_by_language_count = list()
    ngrams_set = set()

    matrix_dict = {} # dict of langage names and nmgra matrices

    master_ngrams = set()
    concepts = set()
    master_concepts_dict = collections.defaultdict(list)

    for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992'):

        concepts_dict = collections.defaultdict(list)
        
        for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id):
            concepts_dict[concept].append(counterpart)

            master_ngrams.update(
                qlc.ngram.words_ngrams_list_for_graphemes_list(
                    o.parse_string_to_graphemes(counterpart)
                    )
                )
            
        master_concepts_dict[wordlistdata_id] = concepts_dict
    
    master_ngrams = list(master_ngrams)
    concepts = list(concepts)
    
    for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key('huber1992'):
        #counterparts = cr.counterpartsForWordlistdataId(wordlistdata_id)
        #print wordlistdata_id
        language_bookname = cr.get_language_bookname_for_wordlistdata_id(wordlistdata_id)
        language_code = cr.get_language_code_for_wordlistdata_id(wordlistdata_id)
                
        matrix = qlc.matrix.Matrix(concepts, master_ngrams)
            
        for i, concept in enumerate(concepts):
            ngrams = qlc.ngram.words_ngrams_list_for_graphemes_list(master_concepts_dict[wordlistdata_id][concept])
            for j, n in enumerate(master_ngrams):
                matrix.matrix[i][j] += 1
        
        matrix_dict[language_bookname] = matrix
    
    # sum up over all languages
    languages = matrix_dict.keys()
    matrix_languages = qlc.matrix.Matrix(languages, master_ngrams)
    for i, l in enumerate(languages):
        matrix_languages.matrix[i] = numpy.sum(matrix_dict[l].matrix, 0)[0]
            
    print(matrix_languages.matrix)
    
    print('Begin comparison of two languages... Bora and Muninane!')
    print()
    
    languages_tuples = [ (u"bora", u"muinane") ]
    
    # for each language to get a matrix of bigrams by meanings
    
    for language1, language2 in languages_tuples:
        matrix1 = matrix_dict[language1]
        matrix2 = matrix_dict[language2]

        master_column_names_set = set(matrix1.column_names+matrix2.column_names)
        master_matrix = qlc.matrix.Matrix(master_column_names_set, master_column_names_set)

        for i in range(matrix1.number_of_rows):
            for j, ngram in enumerate(master_column_names_set):
                for k, ngram in enumerate(master_column_names_set):
                    pass
                    #master_matrix[i][j] += matrix1[.index_for_row_name    

    
if __name__ == "__main__":
    main(sys.argv)