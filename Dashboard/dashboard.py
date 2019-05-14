###########################################
# Libraries
###########################################

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent
import json
import base64

from pandas_datareader import data as web
from datetime import datetime, date, timedelta
import humanize

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

###########################################
# Load data
###########################################

channels = pd.read_csv('info/channels_labeled.csv')
messages = pd.read_csv("info/messages.csv")
messages['count_messages'] = 1
encoded_image = base64.b64encode(open('leftshark.gif', 'rb').read())

# Per module

df = messages.groupby(['module']).sum().reset_index().sort_values(by=['count_reactions'], ascending=True)
df['courses'] = df['module'].apply(lambda mod: "".join([f"- {course}<br>" for course in channels[channels['folder']==mod].actual_name.unique()]))

trace1 = {
				'x': df.module.values,
				'y': df.count_reactions.values,
				'text':[f"Reactions: {num_msg:,d}<br><br>Channels:<br>{courses}" for (num_msg,courses) in zip(df.count_reactions,df.courses)],
				'type': 'bar',
				'opacity': 0.6,
				'marker': dict(color='#73973F',
                            line=dict(color='rgb(3,42,26)',width=1.5,)
                           ),
                'name': 'Reactions',
                'hoverinfo':'text'
				}

trace2 = {
                'x':df.module.values,
                'y':df.count_messages.values,
                'text':[f"Messages: {num_msg:,d}" for num_msg in df.count_messages],
                'type': 'bar',
                'opacity':0.6,
                'marker':dict(color='#E8821E',
                            line=dict(color='rgb(90,55,6)',width=1.5,)
                           ),
                'name':"Messages",
                'hoverinfo':'text',
                
                }
				
# Per channel

df2 = messages.groupby(['course']).sum().reset_index().sort_values(by=['count_reactions'], ascending=True)

def color_per_ch(courses):
	colors = []
	for course in courses:
		if "cats" in course: 
			colors.append("#a8228e")
		elif "dogs" in course:
			colors.append("#a8228e")
		else:
			colors.append("#02b8a0")
	return colors

c = color_per_ch(df2.course.values)
t = [f"Channel: {chan}<br>Module: {messages[messages['course']==chan].module.values[0]}<br>Reactions: {num_msg:,d}" for (chan,num_msg) in zip(df2.course,df2.count_reactions)]
t = [ f"😻😻😻<br>{msg}" if "cats" in msg else msg for msg in t]
t = [ f"🐶🐶🐶<br>{msg}" if "dogs" in msg else msg for msg in t]

trace3 = {
				'x': df2.course.values,
				'y': df2.count_reactions.values,
				'text':t,
				'type': 'bar',
				'opacity': 0.6,
				'marker': dict(color=c,
							line=dict(color='919194',width=1.5,)),
                'name': 'Reactions',
                'hoverinfo':'text'
				}

colors_ds = {
            'mod1_summer': "#FDBB30",
            'mod2_fall1': "#EB821E",
            'mod3_fall2': "#CD542C",
            'mod4_winter': "#00B3D8",
            'mod5_spring1': "#02B8A0",
            'mod6_spring2': "#AED136",
            'mod7_summer': "#73973f",
            'others': "#A8228E",
            'overall': "#DED5B4"
            }
            
options = [{"label": "overall", "value": "overall"}]
options = options + [{"label": channels[channels['folder_name']==name].actual_name.values[0], "value": name} for name in messages.course.unique()]

###########################################
# HTML
###########################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.index_string = '''
<!DOCTYPE html>
<html>
<style>
body{
	background-color: #FFFAF0;
}
h1{
	display: block;
  	font-size: 2em;
  	margin-top: 0.67em;
  	margin-bottom: 0.67em;
  	margin-left: 0;
  	margin-right: 0;
  	font-weight: bold;
  	color: #00543C;
  	text-align: center;
}
</style>
    <head>
        <title>MSDS 2019 - Slack Reactions</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
    	<header>
    		<h1>MSDS 2019 - Slack Reactions</h1>
    	</header>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
        <footer>
            <center>
            	<figure>
            		<hr>
    				<p style="font-size:15px;"><a href="http://vivianamarquez.com" target="_blank">Viviana Márquez</a> © 2019</p> 
    			</figure>
    		</center>
        </footer>
    </body>
</html>
'''

colors = {
	'background': '#FFFAF0',
    'title': '#00543C',
    'subtitle': '#A8228E',
    'text': '#262627'
}

###########################################
# Tab pages
###########################################

# Tab 1 - Reactions per Module/Channel

tab_one = html.Div(className = 'row', children=[
		
	html.Div([
    
    # Graph 1
    dcc.Graph(
        id='graph1',
        )],
		style={
			'marginLeft': 70,
			'marginTop': 20,
			'width': '70%',
			'display': 'inline-block',
			'vertical-align': 'middle',
			'float': 'left'
			}
	),
	
	
	html.Div([
		# Image
		html.Img(src='data:image/gif;base64,{}'.format(encoded_image.decode())),
		
		# Subtitle
    	html.H5('A dashboard for the craziest cohort of all', 
    		style={
        		'textAlign': 'center',
        		'color': colors['subtitle']
    			}
    		),
    		
		# Subtitle
    	html.P('Show number of reactions by...', 
    		style={
        		'textAlign': 'center',
        		'color': colors['text']
    			}
    		),
    		
    	# Dropdown
   		dcc.Dropdown(id="selected-value1",
            options=[{"label": "Module", "value": "Module"},{"label": "Channel", "value": "Channel"}],
            multi=False,
            value="Module",
            placeholder="Reactions by...",
            clearable=False)
		
		],
            style={
            	"width": "20%", 
            	'display': 'inline-block',
            	'vertical-align': 'middle',
            	'horizontal-align': 'middle',
            	'marginRight': 70,
            	'marginTop': 20,
            	'float': 'right',
            	'textAlign': 'center'
            	}
    )
	
])


# Tab 2 - Reactions per day

tab_two = html.Div(className = 'row', children=[
		
	html.Div([
    
    # Graph 1
    dcc.Graph(
        id='graph2',
        )],
		style={
			'marginLeft': 70,
			'marginTop': 20,
			'width': '70%',
			'display': 'inline-block',
			'vertical-align': 'middle',
			'float': 'left'
			}
	),
	
	
	html.Div([
	
		# Subtitle
    	html.P('Show number of reactions by...', 
    		style={
        		'textAlign': 'center',
        		'color': colors['text']
    			}
    		),
    		
    	# Dropdown
   		dcc.Dropdown(id="selected-value2",
            options=options,
            multi=True,
            value=["overall"],
            placeholder="Reactions by...",
            clearable=True
            ),
            
		],
            style={
            	"width": "20%", 
            	'display': 'inline-block',
            	'vertical-align': 'middle',
            	'horizontal-align': 'middle',
            	'marginRight': 70,
            	'marginTop': 20,
            	'float': 'right',
            	'textAlign': 'center'
            	}
    )
	
])


###########################################
# Dashboard Layout
###########################################

app.layout = html.Div([
           	
	# Tabs
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Reactions per Module/Channel', value='tab-1', children=[tab_one]),
        dcc.Tab(label='Reactions per day', value='tab-2', children=[tab_two]),
    ]),
    html.Div(id='tabs-content')
])

###########################################
# Call backs
###########################################

# Tab 1

@app.callback(
    Output('graph1', 'figure'),
    [Input('selected-value1', 'value')]) 
def update_figure(selected):
	if selected=="Module":
		figure = {
				'data': [trace1,trace2],
		        'layout': {
				'title':f"Number of reactions in Slack per module in MSDS",
				'xaxis':{'title': 'Module'},
				'yaxis':{'title': f'Number of reactions'},
				'margin':{'l': 50, 'b': 50, 't': 50, 'r': 50},
				'hovermode':'closest'}
				}
		return figure
	if selected=="Channel":
		figure={'data': [trace3],
		        'layout': {
				'title':f"Number of reactions in Slack per channel in MSDS",
				'xaxis':{'title': 'Channels (Hover for description)','ticks':" ", 'showticklabels':False},
				'yaxis':{'title': f'Number of reactions'},
				'margin':{'l': 50, 'b': 50, 't': 50, 'r': 50},
				'hovermode':'closest',
				'plot_bgcolor': 'white',
                'paper_bgcolor': 'white'
                }
				}
		return figure
		
		
# Tab 2

@app.callback(
    Output('graph2', 'figure'),
    [Input('selected-value2', 'value')]) 
def update_figure(selected):
	trace = []
	for course in selected:
	
		if course == "overall":
			df = messages
			color = colors_ds["overall"]
		
		else:
			df = messages[messages['course']==course]
			color = colors_ds[df.module.unique()[0]]
		
		df = df.groupby(['date']).sum().reset_index()
		df['dow'] = pd.to_datetime(df['date'], format="%Y/%m/%d").dt.day_name()
		t = [f"Reactions: {num_reac}<br>Date: {date}<br>dow: {dow}" for (num_reac,date,dow) in zip(df.count_reactions.values,df.date.values,df.dow.values)]
		
		x = df.date.values
		y = df.count_reactions.values
		
		trace.append(
		go.Scatter(
                    x=x,
                    y=y,
                    text=t,
                    mode='lines+markers', 
                    name=course,
                    opacity=0.8,
                    marker={
                        'size': 3,
                        'color': color,
                    },
                    hoverinfo='text',
                    line={'color': color}
                ) 
        )
	figure = {
				'data': trace,
				'layout': {
					'title': f"Number of reactions per day",
                	'xaxis': {'title': 'Days'},
                	'yaxis': {'title': f'Number of reactions', 'range':[-100, 900]},
                	'margin': {'l': 50, 'b': 50, 't': 50, 'r': 50},
                	'legend': {'x': 1, 'y': 1},
                	'hovermode': 'closest',
					'plot_bgcolor': 'white',
                	'paper_bgcolor': 'white'
            }
        }
	return figure


###########################################
# Main
###########################################

if __name__ == '__main__':
   app.run_server(port=8895)

