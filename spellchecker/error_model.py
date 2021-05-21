import difflib
import re


class ErrorModel:

    def __init__(self, bor, file, alpha=1.5):
        self.bor = bor
        self.alpha = alpha
        self.error_dict = {'replace': {}, 'insert': {}, 'delete': {}}
        self.file = file
        self.__build_model__()

    def __build_model__(self):
        file = open(self.file)
        queries = file.readlines()
        for query in queries:
            ind = query.find('\t')
            if ind > -1:
                orig, fix = query.lower().split('\t')
                if len(re.findall(r'\w+', orig)) == len(re.findall(r'\w+', fix)):
                    self.__add__(fix, orig)

    def __add__(self, fix, orig):
        flag = None
        prev = None
        for line in difflib.ndiff(orig, fix):
            op = line[0]
            letter = line[2]
            orig_letter = None
            fix_letter = None
            if op == '-':
                if flag != 'i':
                    flag = 'd'
                    if letter in self.error_dict['delete']:
                        self.error_dict['delete'][letter] += 1
                    else:
                        self.error_dict['delete'][letter] = 1
                else:
                    flag = 'r'
                    orig_letter = letter
                    fix_letter = prev
            elif op == '+':
                if flag != 'd':
                    flag = 'i'
                    if letter in self.error_dict['insert']:
                        self.error_dict['insert'][letter] += 1
                    else:
                        self.error_dict['insert'][letter] = 1
                else:
                    flag = 'r'
                    orig_letter = prev
                    fix_letter = letter
            if flag == 'r':
                if orig_letter in self.error_dict['replace']:
                    if fix_letter in self.error_dict['replace'][orig_letter]:
                        self.error_dict['replace'][orig_letter][fix_letter] += 1
                    else:
                        self.error_dict['replace'][orig_letter][fix_letter] = 1
                else:
                    self.error_dict['replace'][orig_letter] = {}
                    self.error_dict['replace'][orig_letter][fix_letter] = 1
            prev = letter

    def get_proba(self, word, max_lev=1):
        fix = self.bor.search(word, max_lev)
        for i in range(len(fix)):
            fix[i][1] = self.alpha ** (-fix[i][1])
        return fix
