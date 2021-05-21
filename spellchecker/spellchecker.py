import pickle
import re
from extract_feat import FeatureExtraction
import itertools
import sys


keyboard = {
        'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u',
        'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']', 'ф': 'a', 'ы': 's',
        'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l',
        'ж': ';', 'э': "'", 'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b',
        'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.', 'q': 'й', 'w': 'ц', 'e': 'у',
        'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
        '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п',
        'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э', 'z': 'я',
        'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю',
    }


rus_layout = {'а', 'о', 'у', 'ы', 'э', 'я', 'е', 'ё', 'ю', 'и', 'б', 'в', 'г', 'д',
                   'й', 'ж', 'з', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ъ'}

eng_layout = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                   'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '[', ']', ';', '\'', '\\', ',', '.'}


def get_options(words, lang_model, error_model):
    all_options = []
    eps = 1e-50

    bor_options = []
    for word in words:
        bor_options.append([])
        cur_options = error_model.get_proba(word, max_lev=1.)
        if len(cur_options) == 0:
            cur_options = error_model.get_proba(word, max_lev=2.)
        if len(cur_options) == 0:
            cur_options = [[word, 1.]]
        max_proba1 = -1
        max_proba2 = -1
        for cur_option in cur_options:
            if max_proba1 < cur_option[1]:
                max_proba2 = max_proba1
                max_proba1 = cur_option[1]
            elif max_proba2 < cur_option[1]:
                max_proba2 = cur_option[1]

        bor_options[-1] = [option[0] for option in cur_options if abs(option[1] - max_proba1) <= eps]
        bor_options[-1] += [option[0] for option in cur_options if abs(option[1] - max_proba2) <= eps][:3]
    if len(words) <= 4:
        all_options += itertools.product(*bor_options)
    else:
        all_options += [[option[0] for option in bor_options]]

    layout_options = []
    for word in words:
        try:
            layout_options.append([''.join([keyboard[letter] for letter in word]), word])
        except Exception:
            layout_options.append([word])
    all_options += itertools.product(*layout_options)

    join_options = []
    if len(words) > 1:
        for i in range(len(words) - 1):
            join = words[0:i]
            if (words[i][0] in eng_layout and words[i + 1][0] in eng_layout) or \
                    (words[i][0] in rus_layout and words[i + 1][0] in rus_layout):
                join.append(words[i] + words[i + 1])
            else:
                continue
            join.extend(words[i + 2:])
            join_options.append(join)
        all_options += join_options

    split_options = []
    for i in range(len(words)):
        word = words[i]
        for j in range(1, len(word)):
            split = words[0:i]
            split.append(word[0:j])
            split.append(word[j:])
            split.extend(words[i + 1:])
            split_options.append(split)
    all_options += split_options

    return all_options


class Classifier:
    def __init__(self, clf):
        self.clf = clf

    def predict(self, X):
        return self.clf.predict(X)


if __name__ == "__main__":
    lang_model = open('lang_model.pkl', 'rb')
    lang_model = pickle.load(lang_model)

    error_model = open('error_model.pkl', 'rb')
    error_model = pickle.load(error_model)

    clf = open('clf.pkl', 'rb')
    clf = pickle.load(clf)

    feat_extr = FeatureExtraction(lang_model=lang_model)

    max_iters = 3
    eps = 1e-50
    for query in sys.stdin:
        query_l = query.lower()
        if len(query) == 0:
            print(query)
            continue
        words = re.findall(r'\w+', query_l)
        if len(words) == 0:
            print(query)
            continue
        if clf.predict(feat_extr.get_features(words)) and lang_model.get_query_proba(words) >= 1e-20:
            print(query)
            continue
        vars = []
        for word in words:
            if any(rus_elem in word for rus_elem in rus_layout) and any(eng_elem in word for eng_elem in eng_layout):
                rus_option = ''.join([keyboard[letter] if letter in eng_layout else letter for letter in word])
                eng_option = ''.join([keyboard[letter] if letter in rus_layout else letter for letter in word])
                vars.append([rus_option, eng_option])
            else:
                vars.append([word])
        elder_options = itertools.product(*vars)
        i = 0
        found = False
        while i < max_iters and not found:
            max_proba_approved = None
            best_result_approved = None
            max_proba_possible1 = -1.
            possible_options = []

            for cur_words in elder_options:
                all_options = get_options(list(cur_words), lang_model, error_model)
                for option in all_options:
                    proba = lang_model.get_query_proba(option)
                    possible_options.append((option, proba))
                    if clf.predict(feat_extr.get_features(option)):
                        if max_proba_approved is None or max_proba_approved < proba:
                            max_proba_approved = proba
                            best_result_approved = option
                    if max_proba_possible1 < proba:
                        max_proba_possible1 = proba

            if best_result_approved is not None:
                print(' '.join(best_result_approved))
                found = True
            else:
                elder_options = [list(option[0]) for option in possible_options if
                                          abs(option[1] - max_proba_possible1) < eps][:2]
            i += 1

        if not found:
            print(query)
