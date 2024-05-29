import key2vec
import spacy

from tkinter import Tk
from tkinter import filedialog

root = Tk()
root.withdraw()


#filepath to AI prompt input
glove_path = filedialog.askopenfilename(title="locate glove.6B.xd.txt (x should be a number)")


glove = key2vec.glove.Glove(path = glove_path)
with open('./test.txt', 'r') as f:
    test = f.read()
m = key2vec.key2vec.Key2Vec(test, glove)
m.extract_candidates()
m.set_theme_weights()
m.build_candidate_graph()
ranked = m.page_rank_candidates()

print("Results using glove text file:")

for row in ranked:
    print('{}. {}'.format(row.rank, row.text))


MODEL = "en_core_web_lg"
try:
    nlp = spacy.load(MODEL)
except:
    spacy.cli.download(MODEL)
    nlp = spacy.load(MODEL)



glove = key2vec.glove.Glove(spacy_nlp=nlp,text = test)
m = key2vec.key2vec.Key2Vec(test, glove)
m.extract_candidates()
m.set_theme_weights()
m.build_candidate_graph()
ranked = m.page_rank_candidates()

print("Results using spacy nlp:")

for row in ranked:
    print('{}. {}'.format(row.rank, row.text))