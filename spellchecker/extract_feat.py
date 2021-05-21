import numpy as np


class FeatureExtraction:
    def __init__(self, lang_model):
        self.lang_model = lang_model

    def get_features(self, words):
        query = None
        if len(words) > 1:
            query = ' '.join(words)
        else:
            query = words[0]
        features = [len(words), len(query), self.lang_model.get_query_proba(words)]
        max_proba = 0.
        min_proba = 0.
        probas = [self.lang_model.get_query_proba([word]) for word in words]
        if len(probas):
            max_proba = max(probas)
            min_proba = min(probas)
        correct_words = 0
        if len(words):
            correct_words = sum([word in self.lang_model.probas for word in words])
        features += [max_proba, min_proba, len(words) - correct_words,
                     any(letter in ['`', '[', ']', ';', '\'', '\\', ',', '.', '/'] for letter in query)]
        return np.array(features)[np.newaxis, :]
