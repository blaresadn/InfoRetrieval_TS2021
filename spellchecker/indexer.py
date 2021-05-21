from bor import Bor
from lang_model import LangModel
from error_model import ErrorModel
import pickle
import sys


lang_model = LangModel('queries_all.txt')
lang_model_file = open('lang_model.pkl', 'wb')
pickle.dump(lang_model, lang_model_file)
bor = Bor(lang_model.probas.keys())
sys.setrecursionlimit(50000)
error_model = ErrorModel(bor, 'queries_all.txt')
error_model_file = open('error_model.pkl', 'wb')
pickle.dump(error_model, error_model_file)
