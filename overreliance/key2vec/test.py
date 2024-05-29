import key2vec

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

for row in ranked:
    print('{}. {}'.format(row.rank, row.text))