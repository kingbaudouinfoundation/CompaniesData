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

from functions import parse_contents, create_dataframe
from charts import create_chart_JF, create_chart_age, create_chart_starting_date, create_chart_employees, create_chart_mapbox, create_chart_province

mapbox_access_token = 'pk.eyJ1IjoidGhvbWFzdnJvIiwiYSI6ImNqdWI5Y2JxdjBhYW40NnBpa2RhcHBnb3kifQ.9N4rhGAGmo9zqnXOlt-WOw'

DEFAULT_COLOURS_1 = ['maroon', 'coral', 'darktruquoise', 'chocolate', 'palegoldenrod', 'lightblue']
DEFAULT_COLOURS_2 = ['firebrick', 'lightcoral', 'tomato']
DEFAULT_COLOURS_3 = ['darkred', 'indianred', 'lemonchiffon', 'lightsalmon', 'orange', 'mediumorchid']

LABELS = ['EntityNumber', 'JuridicalForm', 'StartDate', 'Zipcode', 'MunicipalityFR', 'Description', 'employees','latitude', 'longitude', 'province', 'Regions', 'Denomination']

global dframe
dframe = pd.DataFrame(columns = LABELS)

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

app = dash.Dash(__name__)
cache = Cache(app.server, config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 60

app.title = 'Companies Data'

app.layout = html.Div([

    html.Div([
        html.Div([
           
            html.Div(' ', style = {'backgroundColor':'lightgrey', 'height':'50px'}),
            
            html.Div('Change dataset', id = 'top'),
            

            html.Div([

                dcc.Upload(
                    id='upload-data',
                    children = html.Div([
                        'Drag and Drop or ',
                        html.A('Select File', style = {'color':'skyblue','textDecoration':'underline'})
                    ], style = {'color':'black'}),
                    style={
                        'height': '60px','lineHeight':'60px','textAlign': 'center','backgroundColor':'whitesmoke'
                    },
                    multiple=True
                ),

            ], id = "div_up"),

            html.Div([

                        html.Div('FILTERS', style = {'color':'white', 'fontSize':'110%','paddingTop':'60px', 'marginLeft':'20px','fontWeight':'bold'}),
                        html.P('Regions:', style = {'color':'sandybrown', 'marginLeft':'20px','fontWeight':'bold'}),
                        dcc.Dropdown(
                            id = 'regions',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options=[
                                {'label': 'Flandre', 'value': 'Flandre'},
                                {'label': 'Wallonie', 'value': 'Wallonie'},
                                {'label': 'Bruxelles', 'value': 'Bruxelles'}
                                
                            ],
                            multi = 'True'
                        ),

                        html.P('Employees:', style = {'color':'sandybrown','marginLeft':'20px','fontWeight':'bold'}),
                        dcc.Dropdown(
                            id = 'employees',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options = [
                                {'label':'1 to 5', 'value':'1 to 5'},
                                {'label':'5 to 10', 'value':'5 to 10'},
                                {'label':'10 to 20', 'value': '10 to 20'},
                                {'label':'20 to 50', 'value': '20 to 50'},
                                {'label':'50 to 100', 'value': '50 to 100'},
                                {'label':'100 to 500', 'value': '100 to 500'},
                                {'label':'500 to 1000', 'value': '500 to 1000'},
                                {'label':'More than 1000', 'value': 'More than 1000'}
                                
                            ],
                            multi = 'True'
                        )

            ],id = "left2")
        
        ])

    ], id = "left"),

    html.Div([

        html.Div(' ', style = {'backgroundColor':'lightgrey', 'height':'50px'}),
        html.Div('Upload a dataset and see your results below', style = {'color':'mediumvioletred','fontSize':'130%','marginTop':'40px', 'fontWeight':'bold'}),
        html.Div(id='output-data-upload'),
        html.Div(
            id = 'graph1_container',
            children = [
                dcc.Graph(
                    id = 'graph1',
                    figure = create_chart_JF(dframe.copy())
                )
            ]
        ),
        html.Div(
            id = 'graph2_container',
            children = [
                dcc.Graph(
                    id = 'graph2',
                    figure = create_chart_age(dframe.copy())
                )
            ]
        ),
        html.Div(
            id = 'graph3_container',
            children = [
                dcc.Graph(
                    id = 'graph3',
                    figure = create_chart_starting_date(dframe.copy())
                )
            ]
        ),
        html.Div(
            id = 'graph4_container',
            children = [
                dcc.Graph(
                    id = 'graph4',
                    figure = create_chart_employees(dframe.copy())
                )
            ]
        ),
        
        html.Div(
            id = 'graph5_container',
            children = [
                dcc.Graph(
                    id = 'graph5',
                    figure = {
                        'data': [create_chart_mapbox(dframe.copy())],
                        'layout': DEFAULT_LAYOUT
                    },
                )
            ]
        ),
        html.Div(
            id = 'graph6_container',
            children = [
                dcc.Graph(
                    id = 'graph6',
                    figure = create_chart_province(dframe.copy())
                )
            ]
        )
        

    ], id = "right")
 
], id = "body_page")


def filter_df(frame, filters={}):
    if 'regions' in filters and filters['regions'] is not None and len(filters['regions']) > 0:
        frame = frame[frame['Regions'].isin(filters.get('regions'))]
    if 'employees' in filters and filters['employees'] is not None and len(filters['employees']) > 0:
        frame = frame[frame['employees'].isin(filters.get('employees'))]
    
    return frame


@app.callback(
    [Output('graph1_container', 'children'), 
    Output('graph2_container', 'children'),
    Output('graph3_container', 'children'),
    Output('graph4_container', 'children'),
    Output('graph5_container', 'children'),
    Output('graph6_container', 'children')
    ],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
    State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        datas = []
        for r in children:
            datas = r
        global dframe
        dframe = pd.DataFrame(datas, columns = LABELS)

        return [
                dcc.Graph(
                    id = 'graph1',
                    figure = create_chart_JF(dframe.copy())
                )
            ], [
                dcc.Graph(
                    id = 'graph2',
                    figure = create_chart_age(dframe.copy())
                )
            ], [
                dcc.Graph(
                    id = 'graph3',
                    figure = create_chart_starting_date(dframe.copy())
                )
            ], [
                dcc.Graph(
                    id = 'graph4',
                    figure = create_chart_employees(dframe.copy())
                )
            ], [
                dcc.Graph(
                    id = 'graph5',
                    figure = create_chart_mapbox(dframe.copy())
                )
            ], [
                dcc.Graph(
                    id = 'graph6',
                    figure = create_chart_province(dframe.copy())
                )
            ]


@app.callback(
    [Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Output('graph3', 'figure'),
    Output('graph4', 'figure'),
    Output('graph5', 'figure'),
    Output('graph6', 'figure')
    ],
    [Input('regions', 'value'),
     Input('employees', 'value'),
     #Input('juridicalForm', 'value')
     ])
def update_graph(regions, employees):
    
    filters = {
        'regions': regions,
        'employees': employees,
        #'jf': juridicalForm
    }

    filtered_df = filter_df(dframe.copy(), filters)

    return  create_chart_JF(filtered_df), create_chart_age(filtered_df), create_chart_starting_date(filtered_df), create_chart_employees(filtered_df), create_chart_mapbox(filtered_df), create_chart_province(filtered_df)


if __name__ == '__main__':
    app.run_server(debug=True)