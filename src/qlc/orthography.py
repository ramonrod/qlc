# -*- coding: utf-8 -*-

"""
Orthography Profile class for parsing strings into Quantitative Language Comparison format
"""

import sys
import unicodedata

class DuplicateExceptation(Exception): pass

class OrthographyParser(object):
    """
    The orthography profile class for reading in a dictionary's 
    orthography profile and parsing and formating strings into the 
    agreed upon format:

    input string example: uubo
    output string example: # uu b o #
    """

    def __init__(self, orthography_profile):
        """
        Constructor of OrthographyParser class.

        Args:
        - orthography_profile (obligatory): the path to the orthography profile file
        in the file system.

        Returns:
        - nothing

        """
        # read in orthography profile and create a tree structure
        self.root = createTree(orthography_profile)

        # lookup table
        self.graphemeToPhoneme = {}

        # create look up table of grapheme to IPA from orthography profile
        # TODO: move this into a function when we start adding more than just 
        # 2 columns to the orthography profiles

        file = open(orthography_profile, "r", encoding="utf-8")
        line_count = 0
        for line in file:
            line_count += 1
            line = line.strip()

            # skip any comments
            if line.startswith("#") or line == "":
                continue

            line = unicodedata.normalize("NFD", line)
            tokens = line.split(",") # split the orthography profile into columns
            grapheme = tokens[0].strip()
            phoneme = tokens[1].strip()
            
            if not grapheme in self.graphemeToPhoneme:
                self.graphemeToPhoneme[grapheme] = phoneme
            else:
                raise DuplicateException("You have a duplicate in your orthography profile at: {0}".format(line_count))
        file.close()

        # uncomment this line if you want to see the orthography profile tree structure
        # printTree(self.root, "")


    def parse_string_to_graphemes_string_DEPRECATED(self, string):
        string = string.replace(" ", "#") # add boundaries between words
        string = unicodedata.normalize("NFD", string)
        result = ""
        result += printMultigraphs(self.root, string, result+"# ")
        return (True, result)

    def parse_string_to_graphemes_string(self, string):
        """
        Returns the parsed and formated string given the graphemes encoded in the 
        orthography profile.

        Args:
        - string (obligatory): the string to be parsed and formatted

        Returns:    
        - the parsed and formatted string

        For example:
           dog shit => # d o g # sh i t #
        """
        success = True
        parses = []
        string = unicodedata.normalize("NFD", string)
        for word in string.split():
            parse = getParse(self.root, word)
            if len(parse) == 0:
                success = False
                parse = "# <no valid parse> #"
            parses.append(parse)

        # Use "#" as a word boundary token (a special 'grapheme').
        result = "".join(parses).replace("##", "#")  # Ugly. Oh well.
        return (success, result)

    def parse_string_to_graphemes(self, string):
        """
        Accepts a string and returns a orthographically parsed tuple of graphemes.

        Args:
        - string (obligatory): the string to be parsed

        Returns:
        - the parsed string as a tuple of graphemes

        """
        (success, graphemes) = self.parse_string_to_graphemes_string(string)

        return (success, tuple(graphemes.split(" ")))


    def parse_string_to_ipa_string(self, string):
        """
        Returns the parsed and formated string given the graphemes encoded in the 
        orthography profile and the IPA row. Uses a global scrope lookup hash for
        the time being.

        Args:
        - string (obligatory): the string to be parsed and formatted

        Returns:    
        - the parsed and formatted string
        """
        (success, graphemes) = self.parse_string_to_graphemes_string(string)
        if not success:
            return (False, graphemes)
        ipa = graphemes

        # flip the graphemes into phonemes
        # TODO: probably don't need a loop for *every string* -- refactor
        for k, v in self.graphemeToPhoneme.items():
            ipa = ipa.replace(k, v)

        return (True, ipa)
    

# ---------- Tree node --------

class TreeNode(object):
    def __init__(self, char):
        self.char = char
        self.children = {}
        self.sentinel = False

    def isSentinel(self):
        return self.sentinel

    def getChar(self):
        return self.char

    def makeSentinel(self):
        self.sentinel = True

    def addChild(self, char):
        child = self.getChild(char)
        if not child:
            child = TreeNode(char)
            self.children[char] = child
        return child

    def getChild(self, char):
        if char in self.children:
            return self.children[char]
        else:
            return None

    def getChildren(self):
        return self.children

# ---------- Util functions ------
    
def createTree(file_name):
    # Internal function to add a multigraph starting at node.
    def addMultigraph(node, line):
        for char in line:
            node = node.addChild(char)
        node.makeSentinel()

    # Add all multigraphs in each line of file_name. Skip "#" comments and blank lines.
    root = TreeNode('')
    root.makeSentinel()

    #file = codecs.open(file_name, "r", "utf-8")
    file = open(file_name, "r", encoding="utf-8")

    for line in file:
        #print(line.encode("utf-8"))
        line = line.strip()

        # skip any comments
        if line.startswith("#") or line == "":
            continue

        line = unicodedata.normalize("NFD", line)
        tokens = line.split(",") # split the orthography profile into columns
        grapheme = tokens[0]
        addMultigraph(root, grapheme)

    return root

def printMultigraphs(root, line, result):
    # Base (or degenerate..) case.
    if len(line) == 0:
        result += "#"
        return result

    # Walk until we run out of either nodes or characters.
    curr = 0   # Current index in line.
    last = 0   # Index of last character of last-seen multigraph.
    node = root
    while curr < len(line):
        node = node.getChild(line[curr])
        if not node:
            break
        if node.isSentinel():
            last = curr
        curr += 1

    # Print everything up to the last-seen sentinel, and process
    # the rest of the line, while there is any remaining.
    last = last + 1  # End of span (noninclusive).
    result += line[:last]+" "
    return printMultigraphs(root, line[last:], result)

def getParse(root, line):
    parse = getParseInternal(root, line)
    if len(parse) == 0:
        return ""
    return "# " + parse

def getParseInternal(root, line):
    # Base (or degenerate..) case.
    if len(line) == 0:
        return "#"

    parse = ""
    curr = 0
    node = root
    while curr < len(line):
        node = node.getChild(line[curr])
        curr += 1
        if not node:
            break
        if node.isSentinel():
            subparse = getParseInternal(root, line[curr:])
            if len(subparse) > 0:
                # Always keep the latest valid parse, which will be
                # the longest-matched (greedy match) graphemes.
                parse = line[:curr] + " " + subparse

    # Note that if we've reached EOL, but not end of valid grapheme,
    # this will be an empty string.
    return parse

def printTree(root, path):
    for char, child in root.getChildren().items():
        if child.isSentinel():
            char += "*"
        branch = (" -- " if len(path) > 0 else "")
        printTree(child, path + branch + char)
    if len(root.getChildren()) == 0:
        print(path)

# ---------- Main ------

if __name__=="__main__":
    o = OrthographyParser("data/orthography_profiles/thiesen1998.txt")
    test_words = ["aa", "aabuu", "uuabaa auubaa"]
    for word in test_words:
        print("parse_string_to_graphemes_string: ", o.parse_string_to_graphemes_string(word))
        print("parse_string_to_ipa_string: ", o.parse_string_to_ipa_string(word))
        print("parse_string_to_graphemes: ", o.parse_string_to_graphemes(word))
        print()

