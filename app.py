import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc

from util import *

# instantiate and configure Dash app
app = dash.Dash(__name__)
server = app.server
app.title = "SenateGraph"
cyto.load_extra_layouts()


### layout
app.layout = html.Div(id='page', className='row', children=[
    dcc.Store(id='last-hovered'),
    html.Div(id='cyto-canvas', className='col-8 m-0 p-0', children=[
        cyto.Cytoscape( 
            id='cytoscape',
            style={'width': '100%', 'height': '97vh'},
            elements=load_graph(),
            stylesheet=generate_stylesheet(),
        ),
    ]),
    html.Div(className='col-4 p-0 m-0 pr-3 border border-dark', style={'background': 'white'}, children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Data', selected_className='custom-tab--selected', children=[
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
                    
                    html.Br(),
                    html.Div(id='topic-title', children="Topics"),
                    dcc.Dropdown(
                        id='topic-dropdown',
                        options=topic_options(),
                        value='all',
                        clearable=True,
                        multi=True
                    ),

                    html.Br(),
                    html.Div("Show Politcal Parties"),
                    daq.BooleanSwitch(id='node-color-switch', on=True),
                    dbc.Tooltip(
                        "Switch on to color each Senator's node by their political party",
                        target="node-color-switch",
                    ),

                    html.Br(),
                    html.Div("Toggle Dark Mode"),
                    daq.ToggleSwitch(
                        id='dark-theme-switch',
                        label=['Light', 'Dark'],
                        style={'width': '250px', 'margin': 'auto'}, 
                        value=False
                    ),

                ]),
            ]),
            # end of control panel tab
        ]),
    ]),
])


####################
# Callbacks
#####################
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
                                                    height='500px',
                                                    style={'width': '-webkit-fill-available',
                                                            'margin': '10px'}))

            # build, return children
            children.append( 
                html.Div(className='overflow-auto', 
                         style={'height': 'calc(100% - 170px)'},
                         children=tweet_previews)
            )

            return children

@app.callback(Output('page', 'style'),
            [Input('dark-theme-switch', 'value')])
def change_bg(dark_theme):
    if(dark_theme):
        return {'background-color': '#303030'}
    else:
        return {'background-color': 'white'}


if __name__ == '__main__':
    server.run(debug=True)