# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2011, Quantitative Language Comparison Team
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Corpus Reader for data of the project Quantitative Language Comparison.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os.path
import codecs, re, collections


#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

_component_table_columns = dict(name=0, description=1)

_book_table_columns = dict(title=0, author=1, year=2, isbn=3, bibtex_key=4,
                           columns=5, pages=6, origfilepath=7, type=8,
                           is_ready=9)

_dictdata_table_columns = dict(startpage=0, startletters=1, endpage=2,
                               src_language_bookname=3, tgt_language_bookname=4,
                               src_language_id=5, tgt_language_id=6, book_id=7,
                               component_id=8)

_language_table_columns = dict(name=0, langcode=1, description=2, url=3)

_entry_table_columns = dict(head=0, fullentry=1, is_subentry=2,
                            is_subentry_of_entry_id=3, dictdata_id=4,
                            startpage=5, endpage=6, startcolumn=7,
                            endcolumn=8, pos_on_page=9,
                            has_manual_annotations=10)

_annotation_table_columns = dict(entry_id=0, annotationtype_id=1, start=2,
                                 end=3, value=4, string=5)

_wordlistentry_table_columns = dict(fullentry=0, startpage=1, endpage=2,
                                    startcolumn=3, endcloumn=4, pos_on_page=5,
                                    concept_id=6, wordlistdata_id=7,
                                    has_manual_annotations=8)

_wordlistdata_table_columns = dict(startpage=0, endpage=1, language_bookname=2,
                                   language_id=3, book_id=4, component_id=5)

_wordlistconcept_table_columns = dict(concept=0)

_wordlistannotation_table_columns = dict(entry_id=0, annotationtype_id=1,
                                         start=2, end=3, value=4, string=5)

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class CorpusReaderDict(object):
    """
    The corpus reader class for dictionary data. API was designed to allow
    easy access to the data of the dictionaries, all methodes return data
    in Python data structures. Think of it as DB-less queries that return
    Key-Value-Stores.
    """
    
    __slots__ = ("__datapath", "__components", "__books", "__languages", "__dictdata",
                 "__entries", "__annotations", "__entry_annotations_cache",
                 "dictdata_string_ids" )
    
    def __init__(self, datapath):
        """
        Constructor of CorpusReaderDict class.
        
        Parameters
        ----------
        datapath : str
            The path to the dictionary data files (*.csv) in the file system.
        
        Returns
        -------
        Nothing
        """
        
        self.__datapath = datapath
        self.__components = {}
        self.__books = {}
        self.__languages = {}
        self.__dictdata = {}
        self.__entries = {}
        self.__annotations = {}
        self.__entry_annotations_cache = {}
        self.dictdata_string_ids = {}
        
        re_quotes = re.compile('""')

        # read component table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "component.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__components[data.pop(0)] = data

        # read book table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "book.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__books[data.pop(0)] = data

        # read dictdata table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "dictdata.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__dictdata[data.pop(0)] = data
            
        # read entry table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "entry.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            data_stripped = []
            for d in data:
                if len(d) > 0:
                    if d[0] == '"' and d[-1] == '"':
                        d = re_quotes.sub('"', d[1:-1])
                data_stripped.append(d)
            self.__entry_annotations_cache[data_stripped[0]] =\
                collections.defaultdict(set)
            if len(data_stripped) < 7:
                print(data_stripped)
                print(data_stripped[0])
            self.__entries[data_stripped.pop(0)] = data_stripped

        # read annotation table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "annotation.csv"),
                           "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            data_stripped = []
            for d in data:
                if len(d) > 0:
                    if d[0] == '"' and d[-1] == '"':
                        d = re_quotes.sub('"', d[1:-1])
                data_stripped.append(d)
            id = data_stripped.pop(0)
            entry_id = data_stripped[_annotation_table_columns['entry_id']]
            self.__entry_annotations_cache[entry_id][
                # key is the annotation value: "head", "translation", ...
                data_stripped[_annotation_table_columns['value']]
                # value is a list of annotation strings
                ].add(data_stripped[_annotation_table_columns['string']])
            self.__annotations[id] = data_stripped
            
        # read language table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "language.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__languages[data.pop(0)] = data

        self.__init_dictdata_string_ids()


    def __init_dictdata_string_ids(self):
        """
        Initializer for Dictdata identification strings. Dictdata are parts of
        books that contain dictionary data (vs. Nondictdata). The string IDs
        are equal to the ID within URLs of the QuantHistLing website, i.e.
        something like "thiesen1998_10_244". The general structure of the ID is
        "key_startpage_endpage". The strings are saved into a private dict,
        mapping from the numerical ID to the string ID, to allow an easy
        lookup. This method is called by the constructor of the class and
        should not be called by the user.
        
        Parameters
        ----------
        None
            
        Returns
        -------
        Nothing
        """
        for dictdata_id in self.__dictdata:
            book_id = self.__dictdata[dictdata_id][
                      _dictdata_table_columns['book_id']]
            bibtex_key = self.__books[book_id][
                         _book_table_columns['bibtex_key']]
            self.dictdata_string_ids[dictdata_id] = "%s_%s_%s" % \
                (bibtex_key, self.__dictdata[dictdata_id][0],
                 self.__dictdata[dictdata_id][2])

    
    def dictdata_string_id_for_dictata_id(self, dictdata_id):
        """
        Return the string ID to a given numerical ID of a Dictdata entry.
        Dictdata are parts of books that contain dictionary data
        (vs. Nondictdata). The string IDs are equal to the ID within URLs of the
        QuantHistLing website, i.e. something like "thiesen1998_10_244". The
        general structure of the ID is "key_startpage_endpage".
        
        Parameters
        ----------
        dictdata_id : str
            Numerical ID of the Dictdata entry.
        
        Returns
        -------
        String containing the string ID of the given Dictdata entry.
        """
        return self.dictdata_string_ids[dictdata_id]

    def dictdata_ids_for_bibtex_key(self, param_bibtex_key):
        """Return an array of dicionary parts IDs for a given book. The book
        is identified by the so-called bibtex key, which is the string for
        the book from the URL. For example: "thiesen1998".
        
        Parameters
        ----------
        bibtex_key : str
            A string with the bibtex key.
        
        Returns
        -------
        An array containing all the dictdata IDs for the book.
        """
        ret = []
        for dictdata_id in self.__dictdata:
            book_id = self.__dictdata[dictdata_id][
                      _dictdata_table_columns['book_id']]
            if self.__books[book_id][_book_table_columns['bibtex_key']] ==\
               param_bibtex_key:
                ret.append(dictdata_id)
        return ret

    def dictdata_ids_for_component(self, component):
        """Return an array of dicionary parts IDs for a given component. The
        book is identified by the so-called bibtex key, which is the string for
        the book from the URL. For example: "thiesen1998".
        
        Parameters
        ----------
        component : str
            A string with the component's name.
        
        Returns
        -------
        An array containing all the dictdata IDs for the component.
        """
        ret = []
        for dictdata_id in self.__dictdata:
            component_id = self.__dictdata[dictdata_id][
                           _dictdata_table_columns['component_id']]
            if self.__components[component_id][
               _component_table_columns['name']] == component:
                ret.append(dictdata_id)
        return ret
    

    def src_language_iso_for_dictdata_id(self, dictdata_id):
        """
        Returns the source language for the given dictionary part as ISO code.
        
        Parameters
        ----------
        dictdata_id : str
            The ID of the dictionary part to look up
        
        Returns
        -------
        The ISO code of the source language for that bibtex_key.
        """
        src_language_id = self.__dictdata[dictdata_id][
                          _dictdata_table_columns['src_language_id']]
        return self.__languages[src_language_id][
               _language_table_columns['langcode']]
        

    def tgt_language_iso_for_dictdata_id(self, dictdata_id):
        """
        Returns the target language for the given dictionary part as ISO code.
        
        Parameters
        ----------
        dictdata_id : str
            The ID of the dictionary part to look up.
        
        Returns
        -------
        The ISO code of the target language for that bibtex_key
        """
        tgt_language_id = self.__dictdata[dictdata_id][
                          _dictdata_table_columns['tgt_language_id']]
        return self.__languages[tgt_language_id][
               _language_table_columns['langcode']]


    def entry_ids_for_dictdata_id(self, dictdata_id):
        """
        Returns all entry IDs for a given dictdata ID. A dictdata ID is the
        ID of a dictionary part of a source.
        
        Parameters
        ----------
        
        dictdata_id : str
                ID of the dictdata, as Unicode string.
                
        Returns
        -------
        
        A generator for all entry IDs in that dictionary part.
        """
        return(k for k, v in self.__entries.items()
            if v[_entry_table_columns['dictdata_id']] == dictdata_id)


    def annotations_for_entry_id_and_value(self, entry_id, value):
        """
        Returns alls annotation IDs for a given entry ID and and given
        annotation value. Annotation values are strings like "head",
        "translation", etc.
        
        Parameters
        ----------
        
        entry_id : str
                ID of the entry, as Unicode string.
        value : str
                String of the annotation value to look for, i.e. "head",
                "translation", etc.
                
        Returns
        -------
        
        A generator to all the annotatotion of the entry that match the given
        annotation value.
        """
        return(a for a in self.__entry_annotations_cache[entry_id][value])


    def heads_with_translations_for_dictdata_id(self, dictdata_id):
        """
        Returns alls (head, translation) pairs for a given dictdata ID.
        
        Parameters
        ----------
        dictdata_id : str
                ID of the dictdata, as Unicode string.
         
        Returns
        -------
        
        A generator for (head, translation) tuples.
        """
        return((head, translation)\
            for entry_id in self.entry_ids_for_dictdata_id(dictdata_id)
            for head in self.annotations_for_entry_id_and_value(
                        entry_id, "head")
                for translation in self.annotations_for_entry_id_and_value(
                                   entry_id, "translation"))


class CorpusReaderWordlist(object):
    """
    The corpus reader class for wordlist data. API was designed to allow
    easy access to the data of the dictionaries, all methodes return data
    in Python data structures. Think of it as DB-less queries that return
    Key-Value-Stores.
    """
    
    __slots__ = ("__datapath", "__components", "__books", "__languages",
                 "__wordlistdata", "__entries", "__annotations", "__concepts",
                 "__entry_annotations_cache", "wordlistdata_string_ids" )
    
    def __init__(self, datapath):
        """
        Constructor of CorpusReaderWordlist class.
        
        Parameters
        ----------
        datapath : string
            The path to the dictionary data files (*.csv) in the file system.
        
        Returns
        -------
        Nothing
        """
        
        self.__datapath = datapath
        self.__components = {}
        self.__books = {}
        self.__languages = {}
        self.__wordlistdata = {}
        self.__entries = {}
        self.__annotations = {}
        self.__concepts = {}
        self.__entry_annotations_cache = {}
        self.wordlistdata_string_ids = {}

        # read component table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "component.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__components[data.pop(0)] = data

        # read book table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "book.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__books[data.pop(0)] = data

        # read worlistdata table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "wordlistdata.csv"),
                           "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            if len(data) < 7:
                print(data)
            self.__wordlistdata[data.pop(0)] = data

        # read wordlist entry table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "wordlistentry.csv"),
                           "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__entry_annotations_cache[data[0]] = collections.defaultdict(set)
            self.__entries[data.pop(0)] = data

        # read wordlist annotation table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "wordlistannotation.csv"),
                           "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            id = data.pop(0)
            entry_id = data[_wordlistannotation_table_columns['entry_id']]
            self.__entry_annotations_cache[entry_id][
                # key is the annotation value: "head", "translation", ...
                data[_wordlistannotation_table_columns['value']]
                # value is a list of annotation strings
                ].add(data[_wordlistannotation_table_columns['string']])
            self.__annotations[id] = data
            
        # read language table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "language.csv"), "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__languages[data.pop(0)] = data

        # read concept table
        is_first_line = True
        file = codecs.open(os.path.join(datapath, "wordlistconcept.csv"),
                           "r", "utf-8")
        for line in file:
            if is_first_line:
                is_first_line = False
                continue
            line = line.rstrip("\n")
            data = line.split("\t")
            self.__concepts[data.pop(0)] = data

        self.__init_wordlistdata_string_ids()

    def __init_wordlistdata_string_ids(self):
        """
        Initializer for Worlistdata identification strings. Wordlistdata are
        parts of books that contain wordlist data (vs. Nondictdata and
        Dictdata). The string IDs are equal to the ID within URLs of the
        QuantHistLing website, i.e. something like "huber1992_10_392". The
        strings are saved into a private dict, mapping from the numerical ID to
        the string ID, to allow an easy lookup. This method is called by the
        constructor of the class and should not be called by the user.
        
        Parameters
        ----------
        None
            
        Returns
        -------
        Nothing
        """
        for wordlistdata_id in self.__wordlistdata:
            book_id = self.__wordlistdata[wordlistdata_id][
                      _wordlistdata_table_columns['book_id']]
            bibtex_key = self.__books[book_id][
                         _book_table_columns['bibtex_key']]
            self.wordlistdata_string_ids[wordlistdata_id] = "%s_%s_%s" % (
                bibtex_key,
                self.__wordlistdata[wordlistdata_id][
                    _wordlistdata_table_columns['startpage']],
                self.__wordlistdata[wordlistdata_id][
                    _wordlistdata_table_columns['endpage']]
                )
        
    def wordlist_ids_for_bibtex_key(self, bibtex_key):
        """Return an array of wordlist parts IDs for a given book. The book
        is identified by the so-called bibtex key, which is the string for
        the book from the URL. For example: "huber1992".
        
        Parameters
        ----------
        bibtex_key : string
            A string with the bibtex key.

        Returns
        -------
        An iterator over all the wordlistdata IDs for the book.
        """
        ret = []
        for wordlistdata_id in self.__wordlistdata:
            book_id = self.__wordlistdata[wordlistdata_id][
                      _wordlistdata_table_columns['book_id']]
            if self.__books[book_id][_book_table_columns['bibtex_key']] ==\
               bibtex_key:
                ret.append(wordlistdata_id)
        return ret

    def wordlist_ids_for_component(self, component):
        """Return an array of wordlist parts IDs for a given component. The
        book is identified by the so-called bibtex key, which is the string for
        the book from the URL. For example: "huber1992".
        
        Parameters
        ----------
        component : str
            A string with the component's name.
        
        Returns
        -------
        An array containing all the wordlistdata IDs for the component.
        """
        ret = []
        for wordlistdata_id in self.__wordlistdata:
            component_id = self.__wordlistdata[wordlistdata_id][
                           _wordlistdata_table_columns['component_id']]
            
            if component_id and self.__components[component_id][
               _component_table_columns['name']] == component:
                ret.append(wordlistdata_id)
        return ret

    def get_language_bookname_for_wordlist_data_id(self, wordlistdata_id):
        """Returns the language string that is used in the book for a given
        Wordlistdata ID.
        
        Parameters
        ----------
        wordlistdata_id : int
            ID of the wordlistdata part of a book
        
        Returns
        -------
        A string of the language name in the book
        """
        return self.__wordlistdata[wordlistdata_id][
               _wordlistdata_table_columns['language_bookname']]


    def get_language_code_for_wordlist_data_id(self, wordlistdata_id):
        """Returns the language code (ISO ) that was assigned to a source for
        a given wordlistdata ID.
        
        Parameters
        ----------
        wordlistdata_id : int
                ID of the wordlistdata part of a book
        
        Returns
        -------
        A string of the language code of the wordlist data
        """
        language_id = self.__wordlistdata[wordlistdata_id][
                      _wordlistdata_table_columns['language_id']]
        if language_id:
            return self.__languages[language_id][
                   _language_table_columns['langcode']]
        else:
            return ''


    def entry_ids_for_wordlistdata_id(self, wordlistdata_id):
        """
        Returns all entry IDs for a given wordlistdata ID. A wordlistdata ID is
        the ID of a wordlist part of a source.
        
        Parameters
        ----------
        
        wordlistdata_id : str
                ID of the dictdata, as Unicode string.
                
        Returns
        -------
        
        A generator for all entry IDs in that dictionary part.
        """
        return(k for k, v in self.__entries.items()
            if v[_wordlistentry_table_columns['wordlistdata_id']] ==\
               wordlistdata_id)
    
        
    def concept_for_entry_id(self, entry_id):
        return self.__concepts[
            self.__entries[entry_id][
                _wordlistentry_table_columns['concept_id']
                ]][_wordlistconcept_table_columns['concept']]
        
        
    def annotations_for_entry_id_and_value(self, entry_id, value):
        """
        Returns alls annotation IDs for a given entry ID and and given
        annotation value. Annotation values are strings like "head",
        "translation", etc.
        
        Parameters
        ----------
        
        entry_id : str
                ID of the entry, as string.
        value : str
                String of the annotation value to look for, i.e. "head",
                "translation", etc.
                
        Returns
        -------
        
        A generator to all the annotatotion of the entry that match the given
        annotation value.
        """
        return(a for a in self.__entry_annotations_cache[entry_id][value])
    
    
    def counterparts_for_wordlistdata_id(self, wordlistdata_id):
        return(counterpart
            for entry_id in self.entry_ids_for_wordlistdata_id(wordlistdata_id)
                for counterpart in self.annotations_for_entry_id_and_value(
                                   entry_id, "counterpart"))
        

    def concepts_with_counterparts_for_wordlistdata_id(self, wordlistdata_id):
        """Returns all pairs of concepts and counterparts for a given
        wordlistdata ID.
        
        Parameters
        ----------
        
        wordlistdata_id : str
                ID of the wordlistdata, as string.
                
        Returns
        -------
        A generator for all (concept, counterpart) tuples in the wordlist part
        of the source.
        """
        return((self.concept_for_entry_id(entry_id), counterpart)
            for entry_id in self.entry_ids_for_wordlistdata_id(wordlistdata_id)
                for counterpart in self.annotations_for_entry_id_and_value(
                                   entry_id, "counterpart"))

