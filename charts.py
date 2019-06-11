import dash
import base64
import datetime 
from dash.dependencies import Input, Output, State
from operator import itemgetter
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

from functions import get_datas_entities_age, get_datas_starting_date, get_datas_employees, AdaptiveQuery

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
DEFAULT_COLOURS_3 = ['darkgreen', 'green', 'seagreen', 'forestgreen', 'yellowgreen', 'lightgreen', 'chartreuse', 'lime', 'lawngreen']

def create_chart_JF(adQuery = None):

    if adQuery is None:
        return {
            'data': [
                go.Bar(
                    x = [],
                    y = [],
                    marker = {
                        'color': 'cornflowerblue'   
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
    else:
        rows = adQuery.groupby_count('Description')
        if len(rows) > 3:
            s_count = 0
            rows = sorted(rows, key = lambda tup: tup[1], reverse = True)
            to_keep = rows[:3]
            print(to_keep)
            for elt in to_keep:
                if elt in rows:
                    rows.remove(elt)
            for elt in rows:
                s_count = s_count + elt[1]
            to_keep.append(['others', s_count])

            descriptions = []
            descriptions_prop = []
            for elt in to_keep:
                descriptions.append(elt[0])
                descriptions_prop.append(elt[1])
        else:

            descriptions = []
            descriptions_prop = []
            for r in rows:
                descriptions.append(r[0])
                descriptions_prop.append(r[1])
      
        return {
            'data': [
                go.Bar(
                    x = descriptions,
                    y = descriptions_prop,
                    marker = {
                        'color': 'cornflowerblue'  
                    },
                )
            ],
            'layout' : go.Layout(
                margin = go.layout.Margin(
                           t = 100
                    ),
                title = 'Distribution by juridical forms - based on ' + str(adQuery.count()) + ' entities',
                xaxis = go.layout.XAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    showticklabels = True,
                    tickfont=dict(
                    size=7,
                    ),
                ),
                
                yaxis = go.layout.YAxis(
                    showgrid = False,
                    showline = False,
                    zeroline = False,
                    
                )
            )
                
        }

def create_chart_age(adQuery = None):
    xaxis = ['1 to 5 year', '5 to 10 year', '10 to 15 year', '15 to 20 year', 'More than 20 year']

    if adQuery is None:
        return {
            'data': [
                go.Bar(
                    x = xaxis,
                    y = [],
                    marker = {
                        'color': DEFAULT_COLOURS_1  
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
    else:
        
        year = adQuery.get('StartingDate')
        datas = get_datas_entities_age(year)
        
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
                title = 'Entities age - based on ' + str(adQuery.count()) + ' entities',
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

def create_chart_starting_date(adQuery = None):
    
    if adQuery is None:
        return {
            'data' : [
                 go.Bar(
                    x = [],
                    y = [],
                    marker = {
                        'color':'goldenrod'
                    },
                    visible = False
                )

            ],
            'layout' : DEFAULT_LAYOUT
        }
    else:
        xaxis, datas = get_datas_starting_date(adQuery.get('StartingDate'))
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
                title = 'Entities starting dates - based on ' + str(adQuery.count()) + ' entities',
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

def create_chart_employees(adQuery = None):
    if adQuery is None:
        return {
            'data': [
                go.Bar(
                    x = [],
                    y = [],
                    marker = {
                        'color': DEFAULT_COLOURS_3    
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
        
    else:
        rows = adQuery.groupby_count('employees')
        list_emp = []
        emp_prop = []
        for r in rows:
            list_emp.append(r[0])
            emp_prop.append(r[1])
        return {
            'data': [
                go.Bar(
                    x = list_emp,
                    y = emp_prop,
                    marker = {
                        'color': DEFAULT_COLOURS_3    
                    },
                )
            ],
            'layout' : go.Layout(
                title = 'Number of employees - based on ' + str(adQuery.count()) + ' entities',
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

def create_chart_mapbox(adQuery = None):
    

    if adQuery is None:
        return { 
            'data' : [
                go.Scattermapbox(
                    lat = [],
                    lon = [],
                    mode = 'markers',
                    marker=go.scattermapbox.Marker(
                        size=9
                    ),
                    text = [],
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
    else:
        lat = adQuery.get('latitudes')
        lon = adQuery.get('longitudes')
        names = adQuery.get('Denomination')
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
                    title = 'Entities location - based on ' + str(adQuery.count()) + ' entities',
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


def create_chart_province(adQuery = None):
    if adQuery is None:
        return {
            'data': [
                go.Bar(
                    x = [],
                    y = [],
                    marker = {
                        'color':'skyblue'
                    },
                    visible = False
                )
            ],
            'layout' : DEFAULT_LAYOUT
        }
    
    else:
        rows = adQuery.groupby_count('provinces')
        list_prov = []
        prov_prop = []
        for r in rows:
            list_prov.append(r[0])
            prov_prop.append(r[1])
       
        return {
            'data': [
                go.Bar(
                    x = prov_prop,
                    y = list_prov,
                    marker = {
                        'color':'skyblue'
                    },
                    orientation = 'h',
                    
                )
            ],
            'layout' : go.Layout(
                title = 'Distribution by provinces - based on ' + str(adQuery.count()) + ' entities',
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



