# -*- coding: utf-8 -*-  

import sys
import regex
import qlc.ngram
from qlc.orthography import OrthographyParser



"""
examples

jovadyuna > j o v a dy u n a
na jahanunhxa > n a j a h a n un h x a
monno > m o n n o 
"""

test = ["jovadyuna", "na jahanunhxa", "monno"]

file = open("data/dictionaries/heads_with_translations_leach1969_67_161.txt", "r")
file.close()

o = OrthographyParser("data/orthography_profiles/orthography_profile_leach1969.txt")

parsed_test = []

for item in test:
    parsed_counterpart_tuple = o.parse_string_to_ipa_phonemes(item)
    parsed_counterpart = parsed_counterpart_tuple[1]
    ngram_tuples = qlc.ngram.ngrams_from_graphemes(parsed_counterpart,1)
    ngrams_string = qlc.ngram.formatted_string_from_ngrams(ngram_tuples)
    # print(ngrams_string)
    parsed_test.append(ngrams_string)
print(parsed_test)

rules = open("data/orthography_profiles/rules_orthography_profile_leach1969.txt", "r")

for line in rules:
    line = line.strip()
    if line.startswith("#"):
        continue
    
    match_pattern = regex.compile(line)
    
    for word in parsed_test:
        r = match_pattern.search(line)
        print(r.groups())

"""
for word in test:
    for i in range(0, len(regexes)):
        match_pattern = regex.compile(regex[i])
        """
"""
        if not match_pattern.search(word) == None:
            match = match_pattern.sub(match_pattern, replacements[i])
            print(match)
            """
rules.close()

# print(regexes)


"""
s = "aa a n bb ee e n"

match_pattern = ""
for line in regex_file:
    if line.startswith("#"):
        continue
    line = line.strip()

        """
"""
        match = match_pattern.finditer(s)
        for thing in match:
            print(thing.group())
        print(match)
        """


"""
    print(match_pattern)
    print(match_pattern.search(s), "search")
    print(match_pattern.match(s), "match")
    print()

    fp_match = fp.search(line)
    first_population_figure = fp_match.group()
    """

# have to deal with this stuff....


"""
# get data from corpus reader                                                                                                    
cr = CorpusReaderWordlist("data/csv")      # real data 

source = sys.argv[1]

for wordlistdata_id in cr.dictdata_ids_for_bibtex_key(source):
    print(wordlistdata_id)


# o = OrthographyParser("data/orthography_profiles/orthography_profile_leach1969.txt")    
"""

"""
# create generator of corpus reader data                                                                                         
wordlist_iterator = ( (wordlistdata_id, concept, counterpart)
                      for wordlistdata_id in cr.wordlistdata_ids_for_bibtex_key(source)
                      for concept, counterpart in cr.concepts_with_counterparts_for_wordlistdata_id(wordlistdata_id)
                      )

print(wordlistdata_id, concept, counterpart)
"""
