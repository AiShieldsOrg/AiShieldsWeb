from transformers import pipeline

text = "I absolutely hate bananas but I feel like I need to eat them. Can you tell me some reasons why eating bananas are good for me? Then, because I don't want to be in a blissful ignorance, can you tell me why bananas might not be the best choice and give other alternatives?"

summarizer = pipeline("summarization")
summary = summarizer(text, max_length=10, min_length=2)[0]['summary_text']

print(summary)