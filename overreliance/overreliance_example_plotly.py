from overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS
import os
import time

    
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

keyphrase_data_list = ods.get_keyphrases_and_links(input_text, NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS,stopword_list=STOPWORD_LIST)

keyphrase_data_list = ods.get_articles(keyphrase_data_list,site_ignore_list=SITE_IGNORE_LIST)

data_summary_list = ods.compare(keyphrase_data_list,output_text)

end_time = time.time()

print(f"Overreliance algorithm finished in {end_time-start_time:.2f}s")


#=== this is just for plotting
import plotly.graph_objects as go

y = [data['link'] for data in data_summary_list]
x = [data['score'] for data in data_summary_list]

# Create a figure
fig = go.Figure()

# Add a vertical line at x=0
fig.add_vline(x=0, line_color='black', line_dash='dash')

# Add scatter points
fig.add_trace(go.Scatter(x=x, y=y, mode='markers'))

# Annotate points
for i, (x_val, y_val) in enumerate(zip(x, y)):
    index = y_val.find('.com')
    if index != -1:
        new_val = y_val[index + 4:]
    if 'new_val' in locals():
        index = new_val.find('#')
        if index != -1:
            new_val = new_val[:index]
    else:
        new_val = y_val
    if x_val != 0:
        fig.add_vline(x=x_val, line_color='blue', line_dash='solid', opacity=0.3, line_width=1)
        fig.add_annotation(x=x_val, y=y_val, text=new_val, yshift=10, bgcolor='white', bordercolor='black', align='right')
    else:
        fig.add_annotation(x=x_val, y=y_val, text=new_val, yshift=10, bgcolor='white', bordercolor='black')

# Set layout properties
stripped_path = prompt_output_filepath.rpartition('/')[-1][:-4]
fig.update_layout(
    title={
        'text': ANALYSIS_TYPE + " of " + stripped_path + " and user input",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title="Similarity score",
    yaxis_title="Link name",
    yaxis_tickmode='linear',
    yaxis_showticklabels=False,
    width=600,
    height=600,
    xaxis_range=[-1, 1]
)

# Save the figure
#fig.write_image('overreliance_plotly.png', scale=3)

# Show the figure
fig.show()
