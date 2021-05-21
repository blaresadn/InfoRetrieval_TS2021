import re


class LangModel:
    def __init__(self, file):
        self.probas = {}
        self.file = file
        self.words_num = 0
        self.__build_dict__()

    def __build_dict__(self):
        file = open(self.file, 'r')
        queries = file.readlines()
        for query in queries:
            ind = query.find('\t')
            if ind > -1:
                query = query[ind + 1:]
            words = re.findall(r'\w+', query.lower())
            query_len = len(words)
            for i in range(query_len):
                word = words[i]
                if len(word):
                    self.words_num += 1
                    if word in self.probas:
                        self.probas[word]['proba'] += 1
                    else:
                        self.probas[word] = {}
                        self.probas[word]['proba'] = 1
                        self.probas[word]['pairs_dict'] = {}
                    if i < query_len - 1:
                        next_word = words[i + 1]
                        if next_word in self.probas[word]['pairs_dict']:
                            self.probas[word]['pairs_dict'][next_word] += 1
                        else:
                            self.probas[word]['pairs_dict'][next_word] = 1
        for value in self.probas.values():
            value['proba'] /= self.words_num
            pairs_num = sum(value['pairs_dict'].values())
            for word in value['pairs_dict']:
                value['pairs_dict'][word] /= pairs_num

    def get_query_proba(self, query):
        query_len = len(query)
        if query_len < 1 or query_len == 1 and query[0] not in self.probas:
            return 1e-50
        proba = 1
        for i in range(query_len - 1):
            pair = query[i:i + 2]
            cur_proba = 1.
            if pair[0] in self.probas and pair[1] in self.probas[pair[0]]['pairs_dict']:
                cur_proba = 4 * self.probas[pair[0]]['pairs_dict'][pair[1]] * self.probas[pair[0]]['proba']
            elif pair[0] in self.probas:
                cur_proba = 2 * self.probas[pair[0]]['proba'] / self.words_num / len(pair[1]) ** 2
            else:
                cur_proba /= (self.words_num ** 2 * (len(pair[0]) + len(pair[1]) ** 2))
            proba *= cur_proba
        last_word = query[-1]
        if last_word in self.probas:
            proba *= 2 * self.probas[last_word]['proba']
        else:
            proba /= (self.words_num * len(last_word) ** 2)
        return proba
