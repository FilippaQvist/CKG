import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

import plotly.graph_objs as go
from plotly.graph_objs import *
import plotly.figure_factory as FF
import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
import networkx as nx

#app = dash.Dash()

def getPageTitle(title):
    return html.H1(children= title)

def getPageSubtitle(subtitle):
    return html.Div(children=subtitle)

def getBarPlotFigure(data, identifier, title):
    '''This function plots a simple barplot
    --> input:
        - data: is a Pandas DataFrame with three columns: "name" of the bars, 'x' values and 'y' values to plot
        - identifier: is the id used to identify the div where the figure will be generated
        - title: The title of the figure
    --> output:
        Barplot figure within the <div id="_dash-app-content">
    '''
    figure = {}
    figure["data"] = []
    figure["layout"] = {"title":title}
    for name in data.name.unique():
        figure["data"].append({'x': np.unique(data['x'].values), 'y':data.loc[data['name'] == name,'y'].values , 'type': 'bar', 'name': name})

        
    return dcc.Graph(id= identifier, figure = figure)

def getScatterPlotFigure(data, identifier, x, y, x_title, y_title, title):
    '''This function plots a simple Scatterplot
    --> input:
        - data: is a Pandas DataFrame with four columns: "name", x values and y values (provided as variables) to plot
        - identifier: is the id used to identify the div where the figure will be generated
        - title: The title of the figure
    --> output:
        Scatterplot figure within the <div id="_dash-app-content">
    '''
    figure = {}
    figure["data"] = []
    figure["layout"] = go.Layout(title = title,
                                xaxis={'title': x_title},
                                yaxis={'title': y_title},
                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                legend={'x': 0, 'y': 1},
                                hovermode='closest'
                                )
    for name in data.name.unique():
        figure["data"].append(go.Scatter(x = data.loc[data["name"] == name, x], 
                                        y = data.loc[data['name'] == name, y], 
                                        text = name, 
                                        mode = 'markers', 
                                        opacity=0.7,
                                        marker={
                                            'size': 15,
                                            'line': {'width': 0.5, 'color': 'white'}
                                            },
                                        name=name))
       
    return dcc.Graph(id= identifier, figure = figure)


def getHeatmapFigure(data, identifier, title):
    '''This function plots a simple Heatmap
    --> input:
        - data: is a Pandas DataFrame with the shape of the heatmap where index corresponds to rows
            and column names corresponds to columns, values in the heatmap corresponds to the row values
        - identifier: is the id used to identify the div where the figure will be generated
        - title: The title of the figure
    --> output:
        Heatmap figure within the <div id="_dash-app-content">
    '''
    figure = {}
    figure["data"] = []
    figure["layout"] = {"title":title}
    figure['data'].append(go.Heatmap(z=data.values.tolist(),
                                    x = list(data.columns),
                                    y = list(data.index)))
    return dcc.Graph(id = identifier, figure = figure)

def getComplexHeatmapFigure(data, identifier, title):
    figure = FF.create_dendrogram(data.values, orientation='bottom', labels=list(data.columns))
    for i in range(len(figure['data'])):
        figure['data'][i]['yaxis'] = 'y2'
    dendro_side = FF.create_dendrogram(data.values, orientation='right')
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    # Add Side Dendrogram Data to Figure
    figure['data'].extend(dendro_side['data'])

    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))
    data_dist = pdist(data.values)
    heat_data = squareform(data_dist)
    heat_data = heat_data[dendro_leaves,:]
    heat_data = heat_data[:,dendro_leaves]

    heatmap = Data([
        Heatmap(
            x = dendro_leaves,
            y = dendro_leaves,
            z = heat_data,
            colorscale = 'YIGnBu'
        )
    ])

    heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # Add Heatmap Data to Figure
    figure['data'].extend(Data(heatmap))

    # Edit Layout
    figure['layout'].update({'width':800, 'height':800,
                             'showlegend':False, 'hovermode': 'closest',
                             })
    # Edit xaxis
    figure['layout']['xaxis'].update({'domain': [.15, 1],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'ticks':""})
    # Edit xaxis2
    figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                       'mirror': False,
                                   'showgrid': False,
                                   'showline': False,
                                   'zeroline': False,
                                   'showticklabels': False,
                                   'ticks':""}})

    # Edit yaxis
    figure['layout']['yaxis'].update({'domain': [0, .85],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'showticklabels': False,
                                      'ticks': ""})
    # Edit yaxis2
    figure['layout'].update({'yaxis2':{'domain':[.825, .975],
                                       'mirror': False,
                                       'showgrid': False,
                                       'showline': False,
                                       'zeroline': False,
                                       'showticklabels': False,
                                       'ticks':""}})

    return dcc.Graph(id = identifier, figure = figure)


def get3DNetworkFigure(data, sourceCol, targetCol, node_properties, identifier, title):
    '''This function generates a 3D network in plotly
        --> Input:
            - data: Pandas DataFrame with the format: source    target  edge_property1 ...
            - sourceCol: name of the column with the source node
            - targetCol: name of the column with the target node
            - node_properties: dictionary with the properties for each node: {node:{color:..,size:..}}
            - identifier: identifier used to label the div that contains the network figure
            - Title of the plot
    '''
    edge_properties = [c for c in data.columns if c not in [sourceCol, targetCol]]
    graph = nx.from_pandas_dataframe(data, sourceCol, targetCol, edge_properties)
    pos=nx.fruchterman_reingold_layout(graph, dim=3)
    edges = graph.edges()
    N = len(graph.nodes())
    
    Xn=[pos[k][0] for k in pos]
    Yn=[pos[k][1] for k in pos]
    Zn=[pos[k][2] for k in pos]# z-coordinates

    Xed=[]
    Yed=[]
    Zed=[]
    for edge in edges:
        Xed+=[pos[edge[0]][0],pos[edge[1]][0], None]
        Yed+=[pos[edge[0]][1],pos[edge[1]][1], None] 
        Zed+=[pos[edge[0]][2],pos[edge[1]][2], None]

    labels=[]
    colors = []
    sizes = []
    for node in node_properties:
        labels.append(node)
        colors.append(node_properties[node]["color"])
        sizes.append(node_properties[node]["size"])
    
    trace1=Scatter3d(x=Xed,
               y=Yed,
               z=Zed,
               mode='lines',
               line=Line(color='rgb(125,125,125)', width=1),
               hoverinfo='none'
               )
    trace2=Scatter3d(x=Xn,
               y=Yn,
               z=Zn,
               mode='markers',
               name='actors',
               marker=Marker(symbol='dot',
                             size=sizes,
                             color=colors,
                             colorscale='Viridis',
                             line=Line(color='rgb(50,50,50)', width=0.5)
                             ),
               text=labels,
               hoverinfo='text'
               )
    axis=dict(showbackground=False,
          showline=False,
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title=''
          )

    layout = Layout(
         title=title + "(3D visualization)",
         width=1600,
         height=1600,
         showlegend=False,
         scene=Scene(
         xaxis=XAxis(axis),
         yaxis=YAxis(axis),
         zaxis=ZAxis(axis),
        ),
     margin=Margin(
        t=100
    ),
    hovermode='closest',
    annotations=Annotations([
           Annotation(
           showarrow=False,
            text=title,
            xref='paper',
            yref='paper',
            x=0,
            y=0.1,
            xanchor='left',
            yanchor='bottom',
            font=Font(size=14)
            )
        ]),    
    )

    data=Data([trace1, trace2])
    figure=Figure(data=data, layout=layout)
    
    return dcc.Graph(id = identifier, figure = figure)

def appendToDashLayout(data, layout):
    return layout.append(data)


def layoutData(layout):
    app.layout = html.Div(children= layout)


#if __name__ == '__main__':
layout = []
title = getPageTitle("This is a test")
layout.append(title)
subtitle = getPageSubtitle("I am just playing with Dash")
layout.append(subtitle)
data = pd.DataFrame([("a", "1", 2), ("b", "1", 3), ("a","2",12), ("b","2",2)], columns = ["name", "x", "y"])
figure = getBarPlotFigure(data, identifier = "myPlot", title= "Oh what a figure")
layout.append(figure)
data = pd.DataFrame([("Protein 1", 1, 2), ("Protein 2", 1, 3), ("Protein 3", 2, 0.5), ("Protein 4",2 ,4)], columns = ["name", "AS1", "AS2"])
figure2 = getScatterPlotFigure(data, identifier= "myPlot2", x = "AS1", y = "AS2", x_title = "Analytical Sample 1", y_title = "Analytical Sample 2", title = "Correlation Analytical Samples")
layout.append(figure2)
data = pd.DataFrame([("Protein 1", 1, 2, 2, 5), ("Protein 2", 1, 3, 3, 3), ("Protein 3", 2, 0.5, 0, 0.8), ("Protein 4",2 ,4, 10, 20)], columns = ["name", "AS1", "AS2", "AS3", "AS4"])
data = data.set_index("name")
figure3 = getHeatmapFigure(data, identifier = "Heat", title = "What a heatmap!")
layout.append(figure3)    
figure4 = getComplexHeatmapFigure(data, identifier = "Heat 2", title = "WHHHHHHA")
layout.append(figure4)

data = pd.DataFrame([("Protein 1", "Protein 2", 2, 5), ("Protein 2", "Protein 3", 3, 3), ("Protein 3", "Protein 1", 0.5, 0), ("Protein 1","Protein 4" ,4, 10),("Protein 2","Protein 4" ,4, 10),("Protein 1","Protein 5" ,4, 10),("Protein 5","Protein 4" ,4, 10),("Protein 3","Protein 6" ,4, 10),("Protein 6","Protein 4" ,4, 10),("Protein 7","Protein 4" ,4, 10)], columns = ["source", "target", "weight", "score"])
properties = {"Protein 1":{"color":"#edf8fb","size":15}, "Protein 2":{"color":"#bfd3e6", "size":20}, "Protein 3":{"color":"#9ebcda", "size":12}, "Protein 4":{"color":"#8c96c6","size":15}, "Protein 5":{"color":"#8c6bb1", "size":14}, "Protein 6":{"color":"#88419d", "size":13}, "Protein 7":{"color":"#6e016b", "size":18}}
figure5 = get3DNetworkFigure(data, sourceCol = "source", targetCol = "target", node_properties = properties, identifier = "Net", title= "This is a 3D network")
layout.append(figure5)
layoutData(layout)
