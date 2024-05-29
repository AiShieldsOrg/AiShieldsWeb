import key2vec
import spacy

MODEL = "en_core_web_md"
try:
    nlp = spacy.load(MODEL)
except:
    spacy.cli.download(MODEL)
    nlp = spacy.load(MODEL)


with open('./test.txt', 'r') as f:
    test = f.read()
    
glove = key2vec.glove.Glove(spacy_nlp=nlp,text = test)
m = key2vec.key2vec.Key2Vec(test, glove)
m.extract_candidates()
m.set_theme_weights()
m.build_candidate_graph()
ranked = m.page_rank_candidates()

for row in ranked:
    print('{}. {}'.format(row.rank, row.text))