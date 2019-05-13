import dash
import base64
import datetime 
from dash.dependencies import Input, Output, State
from flask_caching import Cache
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import pandas as pd 
import plotly.plotly as py
import plotly.graph_objs as go
import io
import csv 
import sqlite3

from functions import get_datas_entities_age, get_datas_starting_date, get_datas_employees

mapbox_access_token = 'pk.eyJ1IjoidGhvbWFzdnJvIiwiYSI6ImNqdWI5Y2JxdjBhYW40NnBpa2RhcHBnb3kifQ.9N4rhGAGmo9zqnXOlt-WOw'

DEFAULT_LAYOUT = go.Layout(
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    showticklabels=False

                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    showticklabels=False
   
                )
            )


DEFAULT_COLOURS_1 = ['darkblue', 'cornflowerblue', 'darkturquoise', 'lightskyblue', 'steelblue', 'lightblue']
DEFAULT_COLOURS_2 = ['darkred', 'indianred', 'firebrick',  'lightcoral', 'tomato','lightsalmon', 'orange','darkorange','coral','crimson','orangered','darksalmon','brown','chocolate','moccasin','peru']
DEFAULT_COLOURS_3 = ['darkgreen', 'green', 'seagreen', 'forestgreen', 'yellowgreen', 'lightgreen', 'chartreuse', 'lime']

def create_chart_JF(frame):

    descriptionsF = frame[['EntityNumber','Description']].groupby('Description').size().to_frame('count')
    descriptions = descriptionsF.index.tolist()
    descriptions_prop = descriptionsF.loc[: , 'count']

    if len(frame) == 0:
        return {
            'data': [
                go.Bar(
                    x = descriptions,
                    y = descriptions_prop,
                    marker = {
                        'color': DEFAULT_COLOURS_2     
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
    
    if frame is not None:
        return {
            'data': [
                go.Bar(
                    x = descriptions,
                    y = descriptions_prop,
                    marker = {
                        'color': DEFAULT_COLOURS_2     
                    },
                )
            ],
            'layout' : go.Layout(
                margin = go.layout.Margin(
                           t = 100
                    ),
                title = 'Distribution by juridical forms - based on ' + str(len(frame)) + ' entities',
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    showticklabels = False,
                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    
                )
            )
                
        }

def create_chart_age(frame):
    xaxis = ['1 to 5 year', '5 to 10 year', '10 to 15 year', '15 to 20 year', 'More than 20 year']
    year = [d.split('-')[2] for d in frame.loc[: , 'StartDate']]
    datas = get_datas_entities_age(year)

    if len(frame) == 0:
        return {
            'data': [
                go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color': DEFAULT_COLOURS_1  
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
        

    if frame is not None:
        return {
            'data': [
                go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color': DEFAULT_COLOURS_1  
                    },
                )
            ],
            'layout' : go.Layout(
                title = 'Entities age - based on ' + str(len(frame)) + ' entities',
                margin = go.layout.Margin(
                            t=100,
                    ),
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,

                )
            )
        }

def create_chart_starting_date(frame):
    xaxis, datas = get_datas_starting_date(frame.loc[: , 'StartDate'])
    if len(frame) == 0:
        return {
            'data' : [
                 go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color':'goldenrod'
                    },
                    visible = False
                )

            ],
            'layout' : DEFAULT_LAYOUT
        }
        
    if frame is not None: 
        return {
            'data' : [
                 go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color':'goldenrod'
                    },
                )

            ],
            'layout' : go.Layout(
                title = 'Entities starting dates - based on ' + str(len(frame)) + ' entities',
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    showticklabels=False
            
                )
            )
        }

def create_chart_employees(frame):
    xaxis = ['1 to 5', '5 to 10', '10 to 20', '20 to 50', '50 to 100', '100 to 500', '500 to 1000', 'More than 1000']
    datas, list_emp = get_datas_employees(frame.loc[: , "employees"])
    if len(frame) == 0:
        return {
            'data': [
                go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color': DEFAULT_COLOURS_3    
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
        
    if frame is not None:
        return {
            'data': [
                go.Bar(
                    x = xaxis,
                    y = datas,
                    marker = {
                        'color': DEFAULT_COLOURS_3    
                    },
                )
            ],
            'layout' : go.Layout(
                title = 'Number of employees - based on ' + str(len(frame)) + ' entities',
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
            
                )
            )
        }

def create_chart_mapbox(frame):
    lat = frame.loc[: , 'latitude']
    lon = frame.loc[: , 'longitude']
    names = frame.loc[: , 'Denomination']

    if len(frame) == 0:
        return { 
            'data' : [
                go.Scattermapbox(
                    lat = lat,
                    lon = lon,
                    mode = 'markers',
                    marker=go.scattermapbox.Marker(
                        size=9
                    ),
                    text = names,
                    hoverinfo = 'text',
                    visible = False,
                )
            ],
            'layout' : go.Layout(
                    mapbox = go.layout.Mapbox(
                        accesstoken=mapbox_access_token,
                        style = 'mapbox://styles/thomasvro/cjuv6sffh09s01foj7rn28quj',
                        zoom = 7,
                        center=go.layout.mapbox.Center(
                            lat = 51.0,
                            lon = 4.7
                        ),
                    ),
                    
                    margin = go.layout.Margin(
                            l=120,
                            r=120,
                            b=0,
                            t=80,
                            pad=0
                    ),             
                )
        }
        

    if frame is not None:
        return { 
                'data' : [
                    go.Scattermapbox(
                        lat = lat,
                        lon = lon,
                        mode = 'markers',
                        marker=go.scattermapbox.Marker(
                            size=9
                        ),
                        text = names,
                        hoverinfo = 'text',
                    )
                ],
                'layout' : go.Layout(
                    title = 'Entities location - based on ' + str(len(frame)) + ' entities',
                    mapbox = go.layout.Mapbox(
                        accesstoken=mapbox_access_token,
                        style = 'mapbox://styles/thomasvro/cjuv6sffh09s01foj7rn28quj',
                        zoom = 7,
                        center=go.layout.mapbox.Center(
                            lat = 51.0,
                            lon = 4.7
                        ),
                    ),
                    
                    margin = go.layout.Margin(
                            l=120,
                            r=120,
                            b=0,
                            t=80,
                            pad=0
                    ),
                    
                )

         }


def create_chart_province(frame):
    frame_prov = frame[['EntityNumber','province']].groupby('province').size().to_frame('count')
    list_prov = frame_prov.index.tolist()
    prov_prop = frame_prov.loc[: , 'count']

    if len(frame) == 0:
        return {
            'data': [
                go.Bar(
                    x = prov_prop,
                    y = list_prov,
                    marker = {
                        'color':'purple'
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
    
    if frame is not None:
        return {
            'data': [
                go.Bar(
                    x = prov_prop,
                    y = list_prov,
                    marker = {
                        'color':'purple'
                    },
                    orientation = 'h',
                    
                )
            ],
            'layout' : go.Layout(
                title = 'Distribution by provinces - based on ' + str(len(frame)) + ' entities',
                margin = go.layout.Margin(
                    t = 150,
                    r = 180,
                    l = 180,
                    pad = 10,
                ),
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                ),
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    
                )
            )
                
        }

            


        




   
    


