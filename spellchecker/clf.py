from sklearn.linear_model import LogisticRegression
from extract_feat import FeatureExtraction
import pickle
import numpy as np


lang_model = open('lang_model.pkl', 'rb')
lang_model = pickle.load(lang_model)
feat_extract = FeatureExtraction(lang_model)
queries = open('queries_all.txt', 'r')
queries = queries.readlines()
X, y = [], []
for query in queries:
    pair = query.split('\t')
    if len(pair) == 2:
        orig = pair[0].lower()
        if orig[-1] == '\n':
            orig = orig[:-1]
        X.append(feat_extract.get_features(orig))
        y.append(0)
        fix = pair[1].lower()
        if fix[-1] == '\n':
            fix = fix[:-1]
        X.append(feat_extract.get_features(fix))
        y.append(1)
    else:
        orig = pair[0].lower()
        if orig[-1] == '\n':
            orig = orig[:-1]
        X.append(feat_extract.get_features(orig))
        y.append(1)
clf = LogisticRegression()
clf.fit(np.array(X), np.array(y))
