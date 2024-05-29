import plotly.graph_objects as go



def plotter(analysis_type,data_summary_list,prompt_output_filepath):
    
    data_summary_list = sorted(data_summary_list, key=lambda x: x['score'],reverse=False)
    
    y = [data['link'] for data in data_summary_list]
    x = [data['score'] for data in data_summary_list]
    
    caption_list = [f"The cosine similarity is: <b>{score:.2f}</b> for <a href={link} target='_blank'>{link}</a>" for score,link in zip(x,y)]
    caption = '<span style="text-align: left; white-space: pre-line;">'+'<br>'.join(caption_list[::-1]) + '</span>'
    
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

    if analysis_type == "cosine_sim" :
        range = [-1, 1]
        
    if analysis_type == "intersection":
        range = [0, 1]
        
    """ #adding a caption
    fig.add_annotation(
    xref="paper", yref="paper",
    x=0, y=-0.2, # Adjust x and y values to position the text
    xanchor="left", yanchor="top",
    bgcolor='white',
    align='left',
    #text=caption,
    showarrow=False)    """    
    
    # Set layout properties
    stripped_path = prompt_output_filepath.rpartition('/')[-1][:-4]
    fig.update_layout(
        title={
            'text': analysis_type + " of " + stripped_path + " and user input",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="score",
        yaxis_title="Link name",
        yaxis_tickmode='linear',
        yaxis_showticklabels=False,
        width=1000,
        height=600,
        margin=dict(t=80, b=200, l=80, r=200),
        xaxis_range= range
    )

    # Save the figure
    #fig.write_image('overreliance_plotly.png', scale=3)

    # Show the figure
    return fig, caption