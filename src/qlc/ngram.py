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

The orthography.OrthographyParser class returns a tuple of parsed graphemes. 
The functions in this class take a tuple of graphemes as a parameter and parse 
those into various ngram formats, returning 

"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import collections
import numpy
import sys

def ngrams_from_graphemes(graphemes, n=1):
    """
    Takes a tuple of (orthographically parsed) graphemes and returns a tuple of ngrams.

    Default is 1 ngram, i.e. methods will return a tuple of unigrams.

    Note: a word in a dataset should never have less than three elements, 
    e.g. if a word is composed of only one sound (represented by one grapheme, 
    then with the word boundaries ("#"), the length of the word should 
    be at least 3: "#u#". Therefore a tuple of length three will be returned: 
    ("#", "u", "#"). This script will fail if the input tuple is length less 
    than 3.

    Note also that one element tuples (as casted from a list) contain a comma, e.g.:
    >>> l = ["1"]
    >>> print tuple(l)
    ('1',)
    
    Parameters
    ----------
    graphemes: tuple of strings
        a tuple from which the tuple of ngrams is extracted
    n: integer
        the number of graphemes that have to be looked at for the ngram
        default: n = 1 (unigram mode)
        
    Returns
    -------
    a tuple of tupled ngrams for the input string
    """

    # we don't except ngrams less than length 3 (1 sound + 2 word boundaries)
    if len(graphemes) < 3:
        print (graphemes)
        sys.exit("You have a word (with boundaries ('#''s)) that is less than length 3. That's bad!\n")

    list_of_grams = []

    # if more than unigrams
    if n > 1:
        for i in range(0, len(graphemes)-n+1):
            # print("graphemes[i:i+n]", graphemes[i:i+n])
            list_of_grams.append(graphemes[i:i+n])    
            # print("list_of_grams:", list_of_grams)
            # print()
    else:
        for i in range(0, len(graphemes)):
            list_of_grams.append(tuple(graphemes[i]))
    return tuple(list_of_grams)

"""
    print(type(graphemes))
    list_of_grams = []
    for i in range(0, len(graphemes)-n+1):
        print(graphemes[i:i+n])
        list_of_grams.append(graphemes[i:i+n])
    return list_of_grams
    """


def words_ngrams_list_for_graphemes_list(graphemes_list, n=1):
    ngrams_list = []
    for graphemes in graphemes_list:
        ngrams = ngrams_from_graphemes(graphemes, n)
        ngrams_list.extend(ngrams)
    return ngrams_list

def words_ngrams_matrix_for_graphemes_list(graphemes_list, n=1):
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

    matrix = numpy.zeros( (len(row_names), len(ngrams_list)) )
    # matrix = numpy.zeros( ( len(row_names), len(ngrams_list) ) )

    
    # fill the matrix with the ngram counts
    for i in range(len(row_names)):
        for j, ngram in enumerate(ngrams_list):
            matrix[i][j] = ngrams_counts[i][ngram]

    return matrix
        
if __name__ == '__main__':
    # NgramTest().run()
    # tuple = ('#', 'h', 'a', 'd', 'ɯ', '#')
    graphemes = ('#', 'h', '#')
    # string = "#h#"
    print()
    print("ngrams_from_graphemes, tuple:", ngrams_from_graphemes(graphemes, 1))
    print()
