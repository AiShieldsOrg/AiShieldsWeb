import spacy
from spacy import displacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

text = "I absolutely hate bananas but I feel like I need to eat them. Can you tell me some reasons why eating bananas are good for me? Then, because I don't want to be in a blissful ignorance, can you tell me why bananas might not be the best choice and give other alternatives?"
doc = nlp(text)

for token in doc:
    print(token.text, token.dep_, token.morph)
    
html = displacy.render(doc, style="dep")



# Save the HTML to a file
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)
    
