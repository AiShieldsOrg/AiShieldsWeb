from overreliance.overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS

from overreliance.overreliance_plotter import plotter
import time
import plotly.offline as pyo
import spacy

def overreliance_pipeline(input_text, output_text):
    
    print("starting overreliance script...")
    
    SITE_IGNORE_LIST = ["youtube.com","reddit.com","instagram.com","quora.com",".pdf","tiktok.com"]
    NUMBER_OF_SEARCHES = 1
    NUMBER_OF_LINKS = 5
    STOPWORD_LIST = ["*", "$"]
    ANALYSIS_TYPE = "cosine_sim"
    KEYPHRASE_DEPTH = 2
    
    spacy_model = "en_core_web_lg"            
    try:
        spacy_nlp = spacy.load(spacy_model)
    except:
        spacy.cli.download(spacy_model)
        spacy_nlp = spacy.load(spacy_model)
    
    ods = ODS()
    
    start_time = time.time()
    
    sorted_keyphrases = ods.get_keyphrases(input_text, stopword_list=STOPWORD_LIST,keyphrase_depth=KEYPHRASE_DEPTH,method='key2vec',spacy_nlp=spacy_nlp)
    
    keyphrase_data_list = ods.get_links(sorted_keyphrases,search_number_limit=NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS,site_ignore_list=SITE_IGNORE_LIST)
    
    keyphrase_data_list = ods.get_articles(keyphrase_data_list)
    
    data_summary_list = ods.compare(keyphrase_data_list,output_text)
    
    fig1, caption_html = plotter(ANALYSIS_TYPE, data_summary_list, "gpt35-response")
    
    html_div = pyo.plot(fig1, output_type ='div')
    
    end_time = time.time()
    
    print(f'Overreliance calculation time is {end_time-start_time:.2f}s')
    
    return html_div, caption_html