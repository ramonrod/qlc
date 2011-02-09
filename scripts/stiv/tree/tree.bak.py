#!/usr/bin/python                                                                                                                    
import codecs

# ---------- Tree node --------

class TreeNode:
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

    # Add all multigraphs in each line of file_name.
    root = TreeNode('')
    root.makeSentinel()
    file = codecs.open(file_name, "r", "utf-8")
    for line in file:
        line = line.strip()
        addMultigraph(root, line)
    file.close()
    return root

def printMultigraphs(root, line):
    # Base (or degenerate..) case.
    if len(line) == 0:
        print  # Just print a newline.
        return

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
    print line[:last] + " ",
    printMultigraphs(root, line[last:])

def printTree(root, indent):
    children = ""
    for char, child in root.getChildren().iteritems():
        if child.isSentinel():
            char += "*"
        children += char + " "
    print indent + children
    for char, child in root.getChildren().iteritems():
        printTree(child, indent + "  ")

# ---------- Main ------

root = createTree("test_multigraphs.txt")
# printTree(root, "")

file = codecs.open("test_input.txt", "r", "utf-8")
for line in file:
    line = line.strip()
    printMultigraphs(root, line)
