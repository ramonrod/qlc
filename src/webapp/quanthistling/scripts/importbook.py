# -*- coding: utf8 -*-

import sys, os
sys.path.append(os.path.abspath('.'))

import re
import struct
import htmlentitydefs
import unicodedata

from operator import attrgetter

# Pylons model init sequence
import pylons.test
import logging

from quanthistling.config.environment import load_environment
from quanthistling.model.meta import Session, metadata
from quanthistling import model

import quanthistling.dictdata.books

from paste.deploy import appconfig
from sqlalchemy import delete

import importfunctions

dictdata_path = 'quanthistling/dictdata'

##
############################################ helper functions

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def insert_nondictdata_to_db(data, book):
    nondictdata = model.Nondictdata()
    nondictdata.startpage = data['startpage']
    nondictdata.endpage = data['endpage']
    nondictdata.title = data['title']
    file = open(os.path.join(dictdata_path, data['file']), 'r')
    text = file.read()
    file.close()

    if re.search(u"<meta http-equiv=Content-Type content=\"text/html; charset=windows-1252\">", text):
        html = text.decode('windows-1252')
    elif re.search(u"<meta http-equiv=Content-Type content=\"text/html; charset=utf-8\">", text):
        html = text.decode('utf-8')
        
    if book.bibtex_key == 'burtch1983':
        html = re.sub(u"#001", u"ɨ", html)
        html = re.sub(u"#002", u"Ɨ", html)
    elif book.bibtex_key == 'thiesen1998':
        html = re.sub(u"#003", u"-̀", html)
        html = re.sub(u"#004", u"-́", html)
    html = unicodedata.normalize("NFD", html)
    nondictdata.data = html
    nondictdata.book = book

    component = Session.query(model.Component).filter_by(name=data['component']).first()
    if component == None:
        log.warn("Component not found, inserting nondictdata without component." )
    nondictdata.component = component

    Session.add(nondictdata)
    Session.commit()
    return nondictdata

def insert_dictdata_to_db(data, book):
    dictdata = model.Dictdata()
    dictdata.startpage = data['startpage']
    dictdata.endpage = data['endpage']
    dictdata.src_language_bookname = data['src_language_bookname']
    dictdata.tgt_language_bookname = data['tgt_language_bookname']
    dictdata.book = book
    
    srclanguage = Session.query(model.Language).filter_by(name=data['src_language_name']).first()
    if srclanguage == None:
        #log.warn("Language " + b['src_language_name'] + " not found, inserting book " + b['title'].encode('ascii', errors='ingore') + " without source language." )
        log.warn("Language not found, inserting book  without source language." )
    dictdata.src_language = srclanguage
    
    tgtlanguage = Session.query(model.Language).filter_by(name=data['tgt_language_name']).first()
    if tgtlanguage == None:
        #log.warn("Language " + b['tgt_language_name'] + " not found, inserting book " + b['title'] + " without target language." )
        log.warn("Language not found, inserting book without target language." )
    dictdata.tgt_language = tgtlanguage

    component = Session.query(model.Component).filter_by(name=data['component']).first()
    if component == None:
        log.warn("Component not found, inserting dictdata without component." )
    dictdata.component = component
    
    Session.add(dictdata)
    Session.commit()
    return dictdata


##
################################################## Main

def main(argv):
    if len(argv) < 3:
        print "call: importbook.py book_bibtex_key ini_file"
        exit(1)
    
    ini_file = argv[2]
    conf = appconfig('config:' + ini_file, relative_to='.')
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    
    # Create the tables if they don't already exist
    metadata.create_all(bind=Session.bind)

    log = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
        
    book_bibtex_key = unicode(argv[1])
    
    bookdata = [b for b in quanthistling.dictdata.books.list if b['bibtex_key'] == book_bibtex_key][0]
    if bookdata == None:
        print "Error: book not found in booklist file."
        sys.exit(1)

    importfunctions.delete_book_from_db(Session, book_bibtex_key)
    
    book = importfunctions.insert_book_to_db(Session, bookdata)

    for data in bookdata['nondictdata']:
        nondictdata = insert_nondictdata_to_db(data, book)
    
    for data in bookdata['dictdata']:
        
        dictdata = insert_dictdata_to_db(data, book)
    
        log.info("Parsing " + data['file'] + "...")
        f1 = open(os.path.join(dictdata_path, data['file']), 'r')
    
        page                        = 0
        page_new                    = 0
        page_change                 = False
        column                      = 0
        column_new                  = 0
        column_change               = False
        page_found                  = False
        pos_on_page                 = 1
        current_entry_text          = ''
        current_entry_start_page    = 0
        current_entry_page          = 0
        current_entry_start_column  = 0
        current_entry_column        = 0
        current_entry_pos_on_page   = pos_on_page
        current_mainentry_id        = 0
        is_subentry                 = False
        #startletters                = set()
       
        # now process file and add all entries to the database
        re_letter_only = re.compile(data['re_letter_only'], re.DOTALL)
        #print data['re_letter_only']
        
        for line in f1:
            l = line.strip()
            #l = unescape(l)
            l = l.decode('utf-8')
            
            if re.search(r'^<p>', l):
                l = re.sub(r'</?p>', '', l)
                
                # parse page and line number
                if re.match(r'^\[(?:[Ss]palte|[Ss]eite)? ?\d+\]$', l):
                    number = re.sub(r'[\[\]]', '', l)
                    number = re.sub(r'(?:[Ss]palte|[Ss]eite) ?', '', number)
                    number = int(number)
                    if (page_found or re.match(r'\[Spalte', l)) and (not re.match(u'\[Seite', l)):
                        column_new = number
                        page_found = False
                        column_change = True
                        log.info("Column is now: " + str(column_new))
                    else:
                        if bookdata['bibtex_key'] == u"aguiar1994":
                            number = number + 328
                        page_new = number
                        page_found = True
                        if page_new != page:
                            page_change = True
                        log.info("Page is now: " + str(page_new))
                        
                elif re.match(r'^\[BILD\]', l) or re.match(re_letter_only, l):
                    pass
                # parse data
                elif (page_new >= data['startpage']) and (page_new <= data['endpage']):
                    # new entry starts, process previous entry
                    if (re.search(r'<subentry/>', l) or re.search(r'<mainentry/>', l)) and current_entry_text != '':
                        current_entry_text = re.sub(r'[\f\n]*$', '', current_entry_text)
                        entry = importfunctions.process_line(current_entry_text)
                        # add additional entry data
                        entry.startpage               = current_entry_start_page
                        entry.endpage                 = page
                        entry.startcolumn             = current_entry_start_column
                        entry.endcolumn               = column
                        entry.pos_on_page             = current_entry_pos_on_page
                        entry.dictdata                = dictdata
                        entry.is_subentry             = is_subentry
                        entry.is_subentry_of_entry_id = current_mainentry_id
                        Session.add(entry)
                        pos_on_page = pos_on_page + 1
                        if not is_subentry:
                            # add start letter
                            #if (entry.head != None) and (entry.head != ''):
                            #    startletters.add(entry.head[0].lower())
                            # set new main entry id
                            Session.commit()
                            current_mainentry_id = entry.id
                    
                    # only change page and column after processing possible new entry at page
                    # and column start
                    if page_change:
                        page = page_new
                        page_change = False
                        pos_on_page = 1
                        
                    if column_change:
                        column = column_new
                        column_change = False
                    
                    # line is start of a subentry
                    if re.search(r'<subentry/>', l):
                        is_subentry = True
                        l = re.sub(r'<subentry/>', '', l)
                        current_entry_text = ''
                        current_entry_start_page = page
                        current_entry_page = page
                        current_entry_start_column = column
                        current_entry_column = column
                        current_entry_pos_on_page = pos_on_page

                    # line is start of a main entry
                    elif re.search(r'<mainentry/>', l):
                        is_subentry = False
                        l = re.sub(r'<mainentry/>', '', l)
                        current_mainentry_id = 0
                        current_entry_text = ''
                        current_entry_start_page = page
                        current_entry_page = page
                        current_entry_start_column = column
                        current_entry_column = column
                        current_entry_pos_on_page = pos_on_page
    

                    # add page break
                    if page != current_entry_page:
                        current_entry_text = current_entry_text + "\f"
                        current_entry_page = page
                        current_entry_column = column
                    elif column != current_entry_column:
                        current_entry_text = current_entry_text + "\f"
                        current_entry_column = column

                    # add current line to current entry
                    current_entry_text = current_entry_text + l + "\n"
                        
        f1.close()

        #dictdata.startletters = unicode(repr(sorted(list(startletters))))
        Session.commit()
        Session.close()
    
if __name__ == "__main__":
    main(sys.argv)
