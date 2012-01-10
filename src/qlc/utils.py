# -*- coding: utf-8 -*-

# requires that regex package is installed to get "\X" Unicode grapheme match
# http://pypi.python.org/pypi/regex/

import regex
import codecs, unicodedata

def stopwords_from_file(stopwords_filepath = "data/stopwords/spa.txt"):
    stopwords = codecs.open(stopwords_filepath, "r", "utf-8")
    ret = set()
    for line in stopwords:
        word = line.rstrip("\n")
        word = regex.sub(" *\|.*$", "", word)
        if regex.search("[^\s]", word):
            word = unicodedata.normalize("NFD", word)
            ret.add(word)
    return ret

def remove_stopwords(phrase, stopwords):
    re_stopwords = regex.compile(r"\b(?:{0})\b".format( "|".join(stopwords).encode("utf-8") ))
    re_spaces = regex.compile(" +")

    phrase = phrase.strip(" ")
    w_stop = phrase
    if " " in w_stop:
        w_stop = re_stopwords.sub("", w_stop)
        w_stop = w_stop.strip(" ")
        w_stop = re_spaces.sub(" ", w_stop)
    return w_stop
        
def stem_phrase(phrase, stemmer, split_multiwords=False):
    if " " in phrase:
        if split_multiwords:
            ret = []
            for w in phrase.split(" "):
                ret.append(stemmer.stem(w))
            return ret
        else:
            return([])
    elif len(phrase) > 0:
        return [stemmer.stem(phrase)]
    else:
        return([])
    
    
def parseGraphemes(string):
    grapheme_pattern = regex.compile("\X", regex.UNICODE)
    return grapheme_pattern.findall(string)

def storeHash(hash, k):
    if not hash.has_key(k):
        hash[k] = 1
    else:
        hash[k] += 1
    return hash

if __name__=="__main__":
    print("**testing parseGraphemes function")
    print("should return a list: ['a', 'a', 'a', 'a']")
    print("test:", parseGraphemes("aaaa"))
    print
    print("**testing storeHash function")
    print("should return a hash: {'a': 2, 'c': 1, 'b': 1}")
    hash = {"a":1, "b":0}
    storeHash(hash, "a")
    storeHash(hash, "b")
    storeHash(hash, "c")
    print(hash)
    print

