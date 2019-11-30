import urllib
import numpy as np
import json
import math


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
