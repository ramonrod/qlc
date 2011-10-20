# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2011, Quantitative Language Comparison Team
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Ngram reader for graphemes of the project Quantitative Language Comparison.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import collections
import numpy

def ngrams_from_graphemes(graphemes, n=2):
    """
    Goes through the list of graphemes and gathers all the ngrams
    
    Parameters
    ----------
    graphemes: str
        a string from which the list of ngrams is extracted
    n: integer
        the number of graphemes that have to be looked at for the ngram
        default: n = 2 (bigram mode)
        
    Returns
    -------
    a list of ngrams for the input string
    """
    list_of_grams = []
    for i in range(0, len(graphemes)-n+1):
        list_of_grams.append(graphemes[i:i+n])
    return list_of_grams


def words_ngrams_matrix_for_graphemes_list(graphemes_list, n=2):
    """
    Goes through the list of graphemes and gathers all the ngrams
    
    Parameters
    ----------
    grapheme_list: list of strings
        a list of strings from which the list of ngrams is extracted
    n: integer
        the number of graphemes that have to be looked at for the ngram
        default: n = 2 (bigram mode)
        
    Returns
    -------
    row_names: list
        list of strings from the input list (row names of the matrix)
    ngrams_list: list
        list of ngrams that occur in the matrix
    matrix: array
        a matrix of ngrams with the list of graphemes as its rows, the
        list of n-grams as its columns and the counts of each ngram for
        the respective word in the cells
    """
    ngrams_counts = list()
    ngrams_set = set()
    row_names = list()
    # go through the list of words
    for i, graphemes in enumerate(graphemes_list):

        ngrams_counts.append(collections.defaultdict(int))
        row_names.append(graphemes)
        ngrams = ngrams_from_graphemes(graphemes, n)

        # go through the list of ngrams and store them in a set
        for ngram in ngrams:
            ngrams_counts[i][ngram] += 1
            ngrams_set.add(ngram)

    ngrams_list = sorted(list(ngrams_set))
    # generate a matrix with zeros
    matrix = numpy.zeros( ( len(row_names), len(ngrams_list) ) )
    
    # fill the matrix with the ngram counts
    for i in range(len(row_names)):
        for j, ngram in enumerate(ngrams_list):
            matrix[i][j] = ngrams_counts[i][ngram]

    return (row_names, ngrams_list, matrix)
        
if __name__ == '__main__':
    NgramTest().run()