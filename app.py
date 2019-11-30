import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq

import dash_bootstrap_components as dbc

import json
import math
import urllib
import numpy as np

app = dash.Dash(__name__)
server = app.server
app.title = "SenateGraph"
cyto.load_extra_layouts()


## helper functions
def load_graph(importance_threshold=[0,100], selected_senators='all', selected_topics='all'):
    subset_data=[]
    t_low = importance_threshold[0]/100
    t_high = importance_threshold[1]/100

    with open("data/graph.json", 'r') as file:
        data = json.load(file) 

    for d in data:
        if d['type'] == 'edge':
            if d['data']['importance'] >= t_low and d['data']['importance'] <= t_high:
                subset_data.append(d)
        elif d['type'] == 's_node':
            if selected_senators == 'all':
                subset_data.append(d)
            elif d['data']['id'] in selected_senators:
                subset_data.append(d)
        elif d['type'] == 't_node':
            if selected_topics == 'all':
                subset_data.append(d)
            elif d['data']['id'] in selected_topics:
                subset_data.append(d)

    return subset_data

def senator_options():
    with open("data/graph.json", 'r') as file:
        data = json.load(file) 
    options = []
    for d in data:
        if d['type'] == 's_node':
            option = {'label': d['data']['label'], 'value': d['data']['id']}
            options.append(option)

    return options

def topic_options():
    with open("data/graph.json", 'r') as file:
        data = json.load(file) 
    options = []
    for d in data:
        if d['type'] == 't_node':
            option = {'label': d['data']['label'], 'value': d['data']['id']}
            options.append(option)

    return options


def circle_coords(r, center_x, center_y, n_points):
        theta = 2.0*math.pi/n_points
        coords=[]
        for i in range(n_points):
            x_pos = (r*math.cos(theta*i) + center_x)
            y_pos = (r*math.sin(theta*i) + center_y)
            coords.append((x_pos, y_pos))
        return coords

def generate_stylesheet(node_color=False):
    if node_color == True:
        stylesheet=[
                {
                    'selector': 'edge',
                    'style': {
                        'width': 'data(weight)',
                        'color': 'data(color)',
                        'line-color': 'data(color)'
                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(label)',
                        'width': 'data(size)',
                        'height': 'data(size)',
                        'background-color': 'data(color)'
                    }
                },
            ]
    elif node_color==False:
        stylesheet=[
                {
                    'selector': 'edge',
                    'style': {
                        'width': 'data(weight)',
                        'color': 'data(color)',
                        'line-color': 'data(color)'
                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(label)',
                        'width': 'data(size)',
                        'height': 'data(size)',
                    }
                },
            ]
    return stylesheet

def get_tweet_url(senator_id, tweet_id):
    return 'https://twitter.com/{}/status/{}'.format(senator_id, tweet_id)

def encode_url(url):
    return urllib.parse.quote(url)

def get_twitframe_url(encoded_url):
    twitframe_url = "https://twitframe.com/show?url={}".format(encoded_url)
    return twitframe_url

# def generate_iframe(url):
#     tweet_src = "https://twitframe.com/show?url={}".format(url)
#     iframe = "<iframe border=0 frameborder=0 height=250 width=550 src={}></iframe>".format(tweet_src)
#     return iframe

### layout
app.layout = html.Div(className='row', children=[
    dcc.Store(id='last-hovered'),
    html.Div(id='cyto-canvas', className='col-8 m-0 p-0', children=[
        cyto.Cytoscape( 
            id='cytoscape',
            # layout={'name': 'concentric', 
            #         'animate': True, 
            #         'animationDuration': 1000},
            style={'width': '100%', 'height': '97vh'},
            elements=load_graph(),
            stylesheet=generate_stylesheet(),
        ),
    ]),
    html.Div(className='col-4 p-0 m-0 pr-3 border border-dark', style={'background': 'white'}, children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Data', selected_className='custom-tab--selected', children=[

                html.Div(id='mouseover-output'),
                html.Div(id='click-output', className='container', style={'height':'85vh'}),

            
            ]),
            # end of data tab
            dcc.Tab(label='Control Panel', selected_className='custom-tab--selected', children=[
                html.Div(className='containter p-3', children=[
                    
                    html.Br(),
                    html.Div(id='threshold-title', children="% of Tweets about Topic"),
                    dcc.RangeSlider(
                        id = 'threshold-slider',
                        className='pb-5',
                        min=0,
                        max=50,
                        step=5,
                        marks={n:str(n) for n in range(0,51,5)},
                        value=[0, 50]
                    ),
                    dbc.Tooltip(
                        "Choose the cutoffs for the % of each Senator's Tweets",
                        target="threshold-slider",
                    ),

                    html.Br(),
                    html.Div(id='senator-title', children="Senators"),
                    dcc.Dropdown(
                        id='senator-dropdown',
                        options=senator_options(),
                        value='all',
                        clearable=True,
                        multi=True
                    ),
                    # dbc.Tooltip(
                    #     "Choose the cutoffs for the % of each Senator's Tweets",
                    #     target="senator-dropdown",
                    # ),
                    
                    html.Br(),
                    html.Div(id='topic-title', children="Topics"),
                    dcc.Dropdown(
                        id='topic-dropdown',
                        options=topic_options(),
                        value='all',
                        clearable=True,
                        multi=True
                    ),
                    # dbc.Tooltip(
                    #     "Subset the data to view 1 or more political topics",
                    #     target="topic-dropdown",
                    # ),

                    html.Br(),
                    html.Div("Show Politcal Parties"),
                    daq.BooleanSwitch(id='node-color-switch', on=True),
                    dbc.Tooltip(
                        "Switch on to color each Senator's node by their political party",
                        target="node-color-switch",
                    ),
                ]),
            ]),
            # end of control panel tab
        ]),
    ]),
])


######
# Callbacks
#######

@app.callback(Output('cytoscape', 'elements'),
             [Input('threshold-slider', 'value'),
              Input('senator-dropdown', 'value'),
              Input('topic-dropdown', 'value')])
def update_topics(threshold, senators, topics):
    if senators == [] or senators == None:
        senators = 'all'
    if topics == [] or topics == None:
        topics = 'all'
    return load_graph(threshold, senators, topics)


@app.callback(Output('cytoscape', 'layout'),
             [Input('cytoscape', 'elements')],
             [State('senator-dropdown', 'value'),
              State('topic-dropdown', 'value')])
def update_layout(elements, senators, topics):

    if senators == None or senators == []:
        senators = 'all'
    if topics == None or topics == []:
        topics = 'all'
    
    if senators != 'all' and len(senators)==1:
         # get senator position
        senator_node = [element for element in elements if element['data']['id'] == senators[0]][0]
        positions={}
        positions[senator_node['data']['id']] = senator_node['position']
        center_x = senator_node['position']['x']
        center_y = senator_node['position']['y']

        if topics == 'all' or topics == []:
            # get all t_nodes
            t_nodes = [element for element in elements if element['type']=='t_node']
            radius = 300
        else:
            # get selected t_nodes
            t_nodes = [element for element in elements if element['data']['id'] in topics]
            radius = 300

        # get t_node positions
        coordinates = circle_coords(radius, center_x, center_y, len(t_nodes))
        for i, t_node in enumerate(t_nodes):
            t_id = t_node['data']['id']
            position = coordinates[i]
            positions[t_id] = {'x': position[0], 'y': position[1]}
    
        # build layout
        layout = {'name':'preset', 'positions':positions, 'animate': True, 'animationDuration': 1000}
        del elements
        return layout 

    elif topics != 'all' and len(topics)==1:
         # get senator position
        topic_node = [element for element in elements if element['data']['id'] == topics[0]][0]
        positions={}
        positions[topic_node['data']['id']] = topic_node['position']
        center_x = topic_node['position']['x']
        center_y = topic_node['position']['y']

        if senators == 'all' or senators == []:
            # get all s_nodes
            s_nodes = [element for element in elements if element['type']=='s_node']
            radius = 800
        else:
            # get selected s_nodes
            s_nodes = [element for element in elements if element['data']['id'] in senators]
            radius = 800

        # get s_node positions
        coordinates = circle_coords(radius, center_x, center_y, len(s_nodes))
        for i, s_node in enumerate(s_nodes):
            s_id = s_node['data']['id']
            position = coordinates[i]
            positions[s_id] = {'x': position[0], 'y': position[1]}
    
        # build layout
        layout = {'name':'preset', 'positions':positions, 'animate': True, 'animationDuration': 1000}
        del elements
        return layout 

    else:
        layout = {'name':'concentric', 'animate': True, 'animationDuration': 1000}
        return layout
        

@app.callback(Output('senator-dropdown', 'value'),
             [Input('cytoscape', 'tapNodeData')],
             [State('senator-dropdown', 'value')])
def update_senator_dropdown(tap_data, dropdown_val):
    if tap_data and tap_data['group'] != 'topic':
        node_id = tap_data['id']
        if [node_id] == dropdown_val:
            return 'all'
        else:
            return [node_id]

@app.callback(Output('topic-dropdown', 'value'),
             [Input('cytoscape', 'tapNodeData')],
             [State('topic-dropdown', 'value')])
def update_topic_dropdown(tap_data, dropdown_val):
    if tap_data and tap_data['group'] == 'topic':
        node_id = int(tap_data['id'])
        if [node_id] == dropdown_val:
            return 'all'
        else:
            return [node_id]

@app.callback(Output('cytoscape','stylesheet'),
             [Input('node-color-switch', 'on')],
             [State('cytoscape', 'stylesheet')])
def add_node_colors(switch_on, stylesheet):
    return generate_stylesheet(node_color=switch_on)

@app.callback(Output('click-output', 'children'),
             [Input('cytoscape', 'tapEdgeData'),
              Input('cytoscape', 'tapNodeData')],
             [State('cytoscape', 'elements')])
def display_click_data(edge, node, elements):
    if dash.callback_context.triggered[0]['value'] != None:
        if 'group' in dash.callback_context.triggered[0]['value'].keys():
            node_id = dash.callback_context.triggered[0]['value']['id']
            elements = load_graph()
            if dash.callback_context.triggered[0]['value']['group'] == 'topic':
                node_id = int(node_id)
                nodes = [element for element in elements if element['type'] != 'edge']
                node_data = [node for node in nodes if node['data']['id']==node_id][0]['data']
                node_info =  [html.H6(node_data['label'], className='text-center mt-2'),
                                html.Div("Top Keywords: " + node_data['description'], className='text-center')]
            else:
                nodes = [element for element in elements if element['type'] != 'edge']
                node_data = [node for node in nodes if node['data']['id']==node_id][0]['data']
                node_info =  html.H6(node_data['label'] + " " +node_data['description'], className='text-center mt-2')
            return node_info
        else:
            s_id = edge['source']
            t_id = int(edge['target'])
            elements = load_graph()
            nodes = [element for element in elements if element['type'] != 'edge']
            s_node = [node for node in nodes if node['data']['id']==s_id][0]
            t_node = [node for node in nodes if node['data']['id']==t_id][0]

            if edge['prob_conservative'] > 0.50:
                political_lean = "{}% Conservative".format( np.round(100*edge['prob_conservative'], 2) )
            else:
                political_lean = "{}% Liberal".format( np.round(100*(1-edge['prob_conservative']), 2) )

            if edge['sentiment'] > 0.0:
                sentiment = "{}% Positive".format( np.round(100*edge['sentiment'], 2) )
            else:
                sentiment = "{}% Negative".format( np.round(-100*edge['sentiment'], 2) )
            
            children = [
                    html.H6("{} {} stance on {}:".format(s_node['data']['label'], 
                                                            s_node['data']['description'], 
                                                            t_node['data']['label']),
                                                            className='text-center mt-2'),
                    html.H6("{} Tweets".format(edge['weight']), className='text-center'),
                    html.H6(political_lean, className='text-center'),
                    html.H6(sentiment,className='text-center'),
                    html.H6("{}% Subjective".format(np.round(100*edge['subjectivity'])), 
                                                    className='text-center')
            ]
            
            ## tweet previews
            tweets = edge['tweets']
            tweet_ids = list(tweets.keys())
            senator_id = edge['source']
            tweet_previews = []
            for tweet_id in tweet_ids:
                tweet_url = get_tweet_url(senator_id, tweet_id)
                encoded_tweet_url = encode_url(tweet_url)
                twitframe_url = get_twitframe_url(encoded_tweet_url)
                tweet_previews.append( html.Iframe(src=twitframe_url,
                                                    height='auto',
                                                    style={'width': '-webkit-fill-available',
                                                            'margin': '10px'}))

            # build, return children
            children.append( 
                html.Div(className='overflow-auto', 
                         style={'height': 'calc(100% - 170px)'},
                         children=tweet_previews)
            )

            return children


if __name__ == '__main__':
    server.run(debug=True)