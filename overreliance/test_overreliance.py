from overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS
import pandas as pd
from overreliance_plotter import plotter
import time
import webbrowser
from jinja2 import Template
import plotly.offline as pyo




SITE_IGNORE_LIST = ["youtube.com","reddit.com","instagram.com","quora.com",".pdf","tiktok.com"]

SUBJECT_PRONOUNS = ["i","you","he","she","it","we","they"]
OBJECT_PRONOUNS = ["me",""]

PREFIX_CLAUSE_LIST = ["you","I","we","they","me","them","he","him","she","her","your","yours","ours"]

NUMBER_OF_SEARCHES = 1
NUMBER_OF_LINKS = 5
STOPWORD_LIST = ["*", "$"]
ANALYSIS_TYPE = "cosine_sim"
KEYPHRASE_DEPTH = 2


df = pd.read_csv("C:/Users/crossfire234/Desktop/WorkStuff/BCAMP/AiShields/AiShieldsWeb/test/AiShieldsWeb/overreliance/test-data/io-pairs.csv")

input_text_list = list(df["Prompt Input"])
output_text_list = list(df["AI Response"])


ods = ODS()

rows = []

i = 0

for input_text, output_text in zip(input_text_list,output_text_list):
    i+=1
    
    start_time = time.time()

    sorted_keyphrases = ods.get_keyphrases(input_text, stopword_list=STOPWORD_LIST,keyphrase_depth=2)
    
    

    rows.append(repr(sorted_keyphrases))

    keyphrase_data_list = ods.get_links(sorted_keyphrases,search_number_limit=NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS,site_ignore_list=SITE_IGNORE_LIST)

    keyphrase_data_list = ods.get_articles(keyphrase_data_list)

    data_summary_list = ods.compare(keyphrase_data_list,output_text)
    
    end_time = time.time()
    
    print(f'Time taken for loop {i} is {end_time-start_time:.2f}s')


    #intersect_data_summary_list = ods.compare(keyphrase_data_list,output_text,analysis="intersection")
    

    fig1, caption_html = plotter(ANALYSIS_TYPE, data_summary_list, "gpt35-response")

    #fig1.show()
    html_div = pyo.plot(fig1, output_type ='div')
    
    # Using Jinja2
    # Using Jinja2
    

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
    </head>
    <body>
        <h1>{{ heading }}</h1>
        <p>{{ plot | safe }}</p>
        
    </body>
    </html>
    """

    data = {
        "title": "",
        "heading": "",
        "plot": html_div + " " + caption_html
    }

    html = Template(template).render(data)

    # Open the HTML string in a web browser
    
    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("temp.html")
    
    
    
df["keyphrases"] = rows

#df.to_csv("C:/Users/crossfire234/Desktop/WorkStuff/BCAMP/AiShields/AiShieldsWeb/test/AiShieldsWeb/overreliance/test-data/io-pairs.csv",index=False)