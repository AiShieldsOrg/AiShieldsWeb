from overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS
import os
import time
from overreliance_plotter import plotter
from plotly.subplots import make_subplots

    
SITE_IGNORE_LIST = ["youtube.com"]
NUMBER_OF_SEARCHES = 1
NUMBER_OF_LINKS = 20
STOPWORD_LIST = ["*", "$"]
ANALYSIS_TYPE = "cosine_sim"

#=== This portion can be replaced with an interface for prompt/AI output text ===
from tkinter import Tk
from tkinter import filedialog

root = Tk()
root.withdraw()


#filepath to AI prompt input
prompt_input_filepath = filedialog.askopenfilename(title="Find the input prompt text file")

with open(prompt_input_filepath,"r") as f:
    input_text = f.read()
    
prompt_output_filepath = filedialog.askopenfilename(title="Find the AI response text file")
    
with open(prompt_output_filepath,'r') as f:
    output_text = f.read()

start_time = time.time()

ods = ODS()

sorted_keyphrases = ods.get_keyphrases(input_text, stopword_list=STOPWORD_LIST)

keyphrase_data_list = ods.get_links(sorted_keyphrases,search_number_limit=NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS)

keyphrase_data_list = ods.get_articles(keyphrase_data_list,site_ignore_list=SITE_IGNORE_LIST)

data_summary_list = ods.compare(keyphrase_data_list,output_text)


intersect_data_summary_list = ods.compare(keyphrase_data_list,output_text,analysis="intersection")

end_time = time.time()

print(f"Overreliance algorithm finished in {end_time-start_time:.2f}s")


#=== this is just for plotting


fig1 = plotter(ANALYSIS_TYPE, data_summary_list, prompt_output_filepath)
fig2 = plotter("intersection",intersect_data_summary_list,prompt_output_filepath)


fig1.show()
fig2.show()
