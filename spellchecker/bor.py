class Node:

    def __init__(self):
        self.word = None
        self.children = {}

    def insert(self, word):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = Node()
            node = node.children[letter]
        node.word = word


class Bor:

    def __init__(self, words):
        self.tree = Node()
        self.__build_model__(words)

    def __build_model__(self, words):
        for word in words:
            self.tree.insert(word)

    def search(self, word, max_lev=1):
        options = []
        for letter in self.tree.children:
            options += self.__search__(self.tree.children[letter], letter, word, range(len(word) + 1), max_lev)
        return options

    def __search__(self, node, letter, word, prev_row, max_lev):
        cur_options = []
        cur_row = [prev_row[0] + 1]
        for cur_column in range(1, len(word) + 1):
            res = min(cur_row[cur_column - 1] + 1, prev_row[cur_column] + 1)
            if word[cur_column - 1] == letter:
                res = min(res, prev_row[cur_column - 1])
            else:
                res = min(res, prev_row[cur_column - 1] + 1)
            cur_row.append(res)

        if cur_row[-1] <= max_lev and node.word:
            cur_options.append([node.word, cur_row[-1]])

        if min(cur_row) <= max_lev:
            for letter in node.children:
                cur_options += self.__search__(node.children[letter], letter, word, cur_row, max_lev)
        return cur_options
