import matplotlib.pyplot as plt
from overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS
import os

    
SITE_IGNORE_LIST = ["youtube.com"]
NUMBER_OF_SEARCHES = 4
NUMBER_OF_LINKS = 4
STOPWORD_LIST = ["*", "$"]

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


ods = ODS()

keyphrase_data_list = ods.get_keyphrases_and_links(input_text, NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS,stopword_list=STOPWORD_LIST)

keyphrase_data_list = ods.get_articles(keyphrase_data_list,site_ignore_list=SITE_IGNORE_LIST)

data_summary_list = ods.compare(keyphrase_data_list,output_text)

#=== this is just for plotting
y = [data['link'] for data in data_summary_list]
x = [data['score'] for data in data_summary_list]

fig, ax = plt.subplots()
fig.set_figwidth(6)
fig.set_figheight(6)

ax.axvline(x=0, color= 'black',linestyle='--')
ax.scatter(x,y)
for i, (x_val, y_val) in enumerate(zip(x, y)):
    
    index = y_val.find('.com')
    if index != -1:
        new_val = y_val[index + 4:]
        
    index = new_val.find('#')
    if index != -1:
        new_val = new_val[:index]
    
    if x_val != 0:
        ax.axvline(x=x_val, color= 'blue',linestyle='solid',alpha=0.3,linewidth=1)
        ax.annotate(f"{new_val}", (x_val, y_val), xytext=(0, 10), textcoords="offset points",bbox=dict(facecolor='white', edgecolor='black'),ha='right')
    else:
        ax.annotate(f"{new_val}", (x_val, y_val), xytext=(0, 10), textcoords="offset points",bbox=dict(facecolor='white', edgecolor='black'))
ax.set_yticklabels([])


stripped_path = prompt_output_filepath.rpartition('/')[-1][:-4]
print(stripped_path)
ax.set_title("Cosine similarity of " + stripped_path, pad = 20).set_size(20)

ax.set_xlabel('Similarity score', labelpad = 10, fontsize = 12)
ax.set_ylabel('Link name', labelpad = 10, fontsize = 12, loc="bottom")

plt.show()