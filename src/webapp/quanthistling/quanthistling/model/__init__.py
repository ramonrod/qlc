# -*- coding: utf8 -*-

import re
import pickle

"""The application's model objects"""
from quanthistling.model.meta import Session, metadata
from sqlalchemy import schema, types
from sqlalchemy import orm, func

from webhelpers.html import literal
from operator import attrgetter
from pylons import config

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)

entry_table = schema.Table('entry', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('entry_seq_id', optional=True), primary_key=True),
    schema.Column('head', types.Unicode(255)),
    schema.Column('fullentry', types.Text),
    schema.Column('is_subentry', types.Boolean),
    schema.Column('is_subentry_of_entry_id', types.Integer),
    schema.Column('dictdata_id', types.Integer, schema.ForeignKey('dictdata.id')),
    schema.Column('startpage', types.Integer),
    schema.Column('endpage', types.Integer),
    schema.Column('startcolumn', types.Integer),
    schema.Column('endcolumn', types.Integer),
    schema.Column('pos_on_page', types.Integer),
    schema.Column('has_manual_annotations', types.Boolean, default=False)
)

book_table = schema.Table('book', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('book_seq_id', optional=True), primary_key=True),
    schema.Column('title', types.Unicode(255), nullable=False),
    schema.Column('author', types.Unicode(255)),
    schema.Column('year', types.Integer),
    schema.Column('isbn', types.Unicode(255)),
    schema.Column('bibtex_key', types.Unicode(255), nullable=False),
    schema.Column('columns', types.Integer),
    schema.Column('pages', types.Integer),
    schema.Column('origfilepath', types.Unicode(255)),
    schema.Column('type', types.Unicode(255)), # one of: 'dictionary', 'wordlist', 'text'
    schema.Column('is_ready', types.Boolean, default=False),
)

dictdata_table = schema.Table('dictdata', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('dictdata_seq_id', optional=True), primary_key=True),
    schema.Column('startpage', types.Integer),
    schema.Column('startletters', types.Unicode(511)),
    schema.Column('endpage', types.Integer),
    schema.Column('src_language_bookname', types.Unicode(255)),
    schema.Column('tgt_language_bookname', types.Unicode(255)),
    schema.Column('src_language_id', types.Integer, schema.ForeignKey('language.id')),
    schema.Column('tgt_language_id', types.Integer, schema.ForeignKey('language.id')),
    schema.Column('book_id', types.Integer, schema.ForeignKey('book.id')),
    schema.Column('component_id', types.Integer, schema.ForeignKey('component.id')),
)

nondictdata_table = schema.Table('nondictdata', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('nondictdata_seq_id', optional=True), primary_key=True),
    schema.Column('title', types.Unicode(255), nullable=False),
    schema.Column('startpage', types.Integer),
    schema.Column('endpage', types.Integer),
    schema.Column('data', types.Text),
    schema.Column('book_id', types.Integer, schema.ForeignKey('book.id')),
    schema.Column('component_id', types.Integer, schema.ForeignKey('component.id')),
)

wordlistdata_table = schema.Table('wordlistdata', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('wordlistdata_seq_id', optional=True), primary_key=True),
    schema.Column('startpage', types.Integer),
    schema.Column('endpage', types.Integer),
    schema.Column('language_bookname', types.Unicode(255)),
    schema.Column('language_id', types.Integer, schema.ForeignKey('language.id')),
    schema.Column('book_id', types.Integer, schema.ForeignKey('book.id')),
    schema.Column('component_id', types.Integer, schema.ForeignKey('component.id')),
)

annotation_table = schema.Table('annotation', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('annotation_seq_id', optional=True), primary_key=True),
    schema.Column('entry_id', types.Integer, schema.ForeignKey('entry.id'), nullable=False),
    schema.Column('annotationtype_id', types.Integer, schema.ForeignKey('annotationtype.id')),
    schema.Column('start', types.Integer, nullable=False),
    schema.Column('end', types.Integer, nullable=False),
    schema.Column('value', types.Unicode(255)),
    schema.Column('string', types.Unicode(1024)),
)

annotationtype_table = schema.Table('annotationtype', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('annotationtype_seq_id', optional=True), primary_key=True),
    schema.Column('type', types.Unicode(255), nullable=False),
    schema.Column('description', types.Text),
)

language_table = schema.Table('language', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('language_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(255), nullable=False),
    schema.Column('langcode', types.Unicode(10)),
    schema.Column('description', types.Text),
    schema.Column('url', types.Unicode(255)),
)

component_table = schema.Table('component', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('component_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(255), nullable=False),
    schema.Column('description', types.Text),
)

wordlist_entry_table = schema.Table('wordlist_entry', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('wordlist_entry_seq_id', optional=True), primary_key=True),
    schema.Column('fullentry', types.Text),
    schema.Column('startpage', types.Integer),
    schema.Column('endpage', types.Integer),
    schema.Column('startcolumn', types.Integer),
    schema.Column('endcolumn', types.Integer),
    schema.Column('pos_on_page', types.Integer),
    schema.Column('concept_id', types.Integer, schema.ForeignKey('wordlist_concept.id')),
    schema.Column('wordlistdata_id', types.Integer, schema.ForeignKey('wordlistdata.id')),
    schema.Column('has_manual_annotations', types.Boolean, default=False)
)

wordlist_concept_table = schema.Table('wordlist_concept', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('wordlist_concept_seq_id', optional=True), primary_key=True),
    schema.Column('concept', types.Unicode(255)) # the type of the 'concept' depends on the book: may be a spanish/english word, or just a number, or...
)

wordlist_annotation_table = schema.Table('wordlist_annotation', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('wordlist_annotation_seq_id', optional=True), primary_key=True),
    schema.Column('entry_id', types.Integer, schema.ForeignKey('wordlist_entry.id'), nullable=False),
    schema.Column('annotationtype_id', types.Integer, schema.ForeignKey('annotationtype.id')),
    schema.Column('start', types.Integer, nullable=False),
    schema.Column('end', types.Integer, nullable=False),
    schema.Column('value', types.Unicode(255)),
    schema.Column('string', types.Unicode(1024)),
)

corpusversion_table = schema.Table('corpusversion', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('corpusversion_seq_id', optional=True), primary_key=True),
    schema.Column('version', types.Integer, nullable=False),
    schema.Column('revision', types.Integer, nullable=False),
    schema.Column('updated', types.DateTime)
)

class Entry(object):
                    
    def append_annotation(self, start, end, value, type, string=None):
        annotation = Annotation()
        
        annotation.start = start
        annotation.end   = end
        annotation.value = value
        if string == None:
            annotation.string = self.fullentry[start:end].strip()
        else:
            annotation.string = string
        annotationtype_q = Session.query(Annotationtype)
        annotationtype = annotationtype_q.filter_by(type=type).first()
        annotation.annotationtype = annotationtype
        self.annotations.append(annotation)
        
    def annotations_sorted_by_type_and_start(self, types = ['dictinterpretation', 'orthographicinterpretation', 'formatting', 'pagelayout', 'errata']):
        ret = []
        for type in types:
            ret2 = []
            for a in self.annotations:
                if a.annotationtype.type == type:
                    ret2.append(a)
            ret2 = sorted(ret2, key=attrgetter('start'))
            ret.extend(ret2)
        return ret
        #return sorted(self.annotations, key=attrgetter('annotationtype.type', 'start'))

    def subentries(self):
        entries_q = Session.query(Entry)
        subentries = entries_q.filter_by(is_subentry_of_entry_id=self.id).all()
        return subentries

    def mainentry(self):
        entry = Session.query(Entry).filter_by(id=self.is_subentry_of_entry_id).first()
        return entry

    def fullentry_with_formatting(self, type = 'html', page = None, column = None):
        text = self.fullentry + ' '
        i = 0
        offset = 0
        for char in text:
            
            annotations_pagelayout = []
            annotations_formatting_start = []
            annotations_formatting_end = []
            for a in self.annotations:
                if a.annotationtype.type == 'pagelayout':
                    if a.start == i or a.end == i:
                        annotations_pagelayout.append(a)
                elif a.annotationtype.type == 'formatting':
                    if a.start == i:
                        annotations_formatting_start.append(a)
                    elif a.end == i:
                        annotations_formatting_end.append(a)
                        
            for a in annotations_pagelayout:
                insert_position = i + offset
#                if type == 'html':
#                    if (a.value == 'tab') and ('hyphen' and 'newline' not in [a.value for a in annotations_pagelayout]):
#                        text = text[:insert_position] + u' ' + text[insert_position:]
#                        offset = offset + 1
#                    if (a.value == 'newline') or (a.value == 'pagebreak'):
#                        has_hyphen = False
#                        for a2 in annotations_pagelayout:
#                            if a2.value == 'hyphen':
#                                has_hyphen = True
#                        if not has_hyphen:
#                            text = text[:insert_position] + u' ' + text[insert_position:]
#                            offset = offset + 1
                if type == 'html_with_layout':
                    if (a.value == 'newline'):
                        text = text[:insert_position] + u'<br/>' + text[insert_position:]
                        offset = offset + 5
                    elif (a.value == 'hyphen'):
                        text = text[:insert_position] + u'-' + text[insert_position:]
                        offset = offset + 1
                        insert_position = insert_position + 1
                    elif (a.value == 'tab'):
                        text = text[:insert_position] + u'&nbsp;&nbsp;&nbsp;&nbsp;' + text[insert_position:]
                        offset = offset + 24
                    elif (a.value == 'pagebreak'):
                        if (page and (self.startpage != page)) or (column and (self.startcolumn != column)):
                            textnew = text[insert_position:]
                            html = text[:insert_position]
                            start_tags = re.findall(r'<(?!/).*?>', html)
                            start_tags = [ t for t in start_tags if not re.search('/>$', t)]
                            end_tags = re.findall(r'</.*?>', html)
                            start_tags = [ re.sub(r'[<>]', '', t) for t in start_tags]
                            end_tags = [ re.sub(r'[<>/]', '', t) for t in end_tags]
                            html = ''
                            for t in start_tags:
                                if t in end_tags:
                                    end_tags.remove(t)
                                else:
                                    html = html + '<' + t + '>'
                            offset = -i + len(html)
                            text = html + textnew
                        elif (page and (self.endpage != page)) or (column and (self.endcolumn != column)):
                            text = text[:insert_position]
                            start_tags = re.findall(r'<(?!/).*?>', text)
                            start_tags = [ t for t in start_tags if not re.search('/>$', t)]
                            end_tags = re.findall(r'</.*?>', text)
                            start_tags = [ re.sub(r'[<>]', '', t) for t in start_tags]
                            end_tags = [ re.sub(r'[<>/]', '', t) for t in end_tags]
                            for t in start_tags:
                                if t in end_tags:
                                    end_tags.remove(t)
                                else:
                                    text = text + '</' + t + '>'
                            return literal(text)
                                
            for a in annotations_formatting_end:
                insert_position = i + offset
                if (type == 'html') or (type == 'html_with_layout'):
                    if (a.value == 'bold'):
                        text = text[:insert_position] + u'</b>' + text[insert_position:]
                        offset = offset + 4
                    elif (a.value == 'italic'):
                        text = text[:insert_position] + u'</i>' + text[insert_position:]
                        offset = offset + 4
                    elif (a.value == 'underline'):
                        text = text[:insert_position] + u'</u>' + text[insert_position:]
                        offset = offset + 4
                    elif (a.value == 'underline'):
                        text = text[:insert_position] + u'</u>' + text[insert_position:]
                        offset = offset + 4
                    elif (a.value == 'superscript'):
                        text = text[:insert_position] + u'</sup>' + text[insert_position:]
                        offset = offset + 6
                    elif (a.value == 'smallcaps'):
                        text = text[:insert_position] + u'</span>' + text[insert_position:]
                        offset = offset + 7

            for a in annotations_formatting_start:
                insert_position = i + offset
                if (type == 'html') or (type == 'html_with_layout'):
                    if (a.value == 'bold'):
                        text = text[:insert_position] + u'<b>' + text[insert_position:]
                        offset = offset + 3
                    elif (a.value == 'italic'):
                        text = text[:insert_position] + u'<i>' + text[insert_position:]
                        offset = offset + 3
                    elif (a.value == 'underline'):
                        text = text[:insert_position] + u'<u>' + text[insert_position:]
                        offset = offset + 3                        
                    elif (a.value == 'superscript'):
                        text = text[:insert_position] + u'<sup>' + text[insert_position:]
                        offset = offset + 5     
                    elif (a.value == 'smallcaps'):
                        text = text[:insert_position] + u'<span style="font-variant: small-caps">' + text[insert_position:]
                        offset = offset + 39
                        
            i = i + 1
        return literal(text[:-1])

class Book(object):
    
    def bookinfo_with_status(self):
        bookinfo = "%s. %s. %s" % (self.author, self.year, self.title)
        color = "red"    
        if self.is_ready:
            color = "green"
        bookinfo = bookinfo + literal(" <span style=\"color:%s;\">&bull;</span>" % color)
        return bookinfo

    def bookinfo(self):
        return "%s. %s. %s" % (self.author, self.year, self.title)

    def wordlistdata_startpage(self):
        if self.type == 'wordlist':
            return Session.query(func.max(Wordlistdata.startpage)).filter_by(book_id=self.id).scalar()
        else:
            return None
        
    def wordlistdata_endpage(self):
        if self.type == 'wordlist':
            return Session.query(func.max(Wordlistdata.endpage)).filter_by(book_id=self.id).scalar()
        else:
            return None

class Dictdata(object):
    pass

class Nondictdata(object):

    def title_url(self):
        return re.sub(u" ", "_", self.title.lower())

class Wordlistdata(object):
    pass
        
class Annotation(object):
    pass

class Annotationtype(object):
    pass

class Language(object):
    pass

class Component(object):
    
    def books(self):
        books = set()
        for data in self.dictdata:
            books.add(data.book)
        for data in self.nondictdata:
            books.add(data.book)
        for data in self.wordlistdata:
            books.add(data.book)
        list_books = list(books)
        list_books = sorted(list_books, key=attrgetter('bibtex_key'))
        return list_books

class Corpusversion(object):
    pass

class WordlistEntry(Entry):
                   
    def append_annotation(self, start, end, value, type, string=None):
        annotation = WordlistAnnotation()
        
        annotation.start = start
        annotation.end   = end
        annotation.value = value
        if string == None:
            annotation.string = self.fullentry[start:end].strip()
        else:
            annotation.string = string
    
        annotationtype_q = Session.query(Annotationtype)
        annotationtype = annotationtype_q.filter_by(type=type).first()
        #if not annotationtype:
        #    print "No such annotation type: %s" % type
        annotation.annotationtype = annotationtype
        annotation.entry_id = self.id
        self.annotations.append(annotation)

    def subentries(self):
        return []

    def mainentry(self):
        return []

class WordlistConcept(object):
    pass

class WordlistAnnotation(object):
    pass

orm.mapper(Entry, entry_table, properties={
   'annotations':orm.relation(Annotation, backref='entry')
})

orm.mapper(Book, book_table, properties={
   'dictdata':orm.relation(Dictdata, backref='book'),
   'nondictdata':orm.relation(Nondictdata, backref='book'),
   'wordlistdata':orm.relation(Wordlistdata, backref='book')
})

orm.mapper(Component, component_table, properties={
   'dictdata':orm.relation(Dictdata, backref='component'),
   'nondictdata':orm.relation(Nondictdata, backref='component'),
   'wordlistdata':orm.relation(Wordlistdata, backref='component')
})

orm.mapper(Annotation, annotation_table)

orm.mapper(Annotationtype, annotationtype_table, properties={
   'annotations':orm.relation(Annotation, backref='annotationtype'),
   'wordlist_annotations':orm.relation(WordlistAnnotation, backref='annotationtype')
})

orm.mapper(Language, language_table, properties={
   'dictdata_with_src':orm.relation(Dictdata, primaryjoin=language_table.c.id == dictdata_table.c.src_language_id, backref="src_language"),
   'dictdata_with_tgt':orm.relation(Dictdata, primaryjoin=language_table.c.id == dictdata_table.c.tgt_language_id, backref="tgt_language"),
   'wordlistdata':orm.relation(Wordlistdata, backref='language')
})

orm.mapper(Dictdata, dictdata_table, properties={
   'entries':orm.relation(Entry, backref='dictdata')
})

orm.mapper(Nondictdata, nondictdata_table)

orm.mapper(Wordlistdata, wordlistdata_table, properties={
    'entries': orm.relation(WordlistEntry, backref="wordlistdata")
})

orm.mapper(WordlistEntry, wordlist_entry_table, properties={
   'annotations':orm.relation(WordlistAnnotation, backref='entry')
})

orm.mapper(WordlistConcept, wordlist_concept_table, properties={
    'entries': orm.relation(WordlistEntry, backref="concept")
})

orm.mapper(WordlistAnnotation, wordlist_annotation_table)

orm.mapper(Corpusversion, corpusversion_table)
