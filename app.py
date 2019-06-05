
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

from functions import get_info, build_filters, parse_contents, create_dataframe, AdaptiveQuery
from charts import create_chart_JF, create_chart_age, create_chart_starting_date, create_chart_employees, create_chart_mapbox, create_chart_province

mapbox_access_token = 'pk.eyJ1IjoidGhvbWFzdnJvIiwiYSI6ImNqdWI5Y2JxdjBhYW40NnBpa2RhcHBnb3kifQ.9N4rhGAGmo9zqnXOlt-WOw'

LABELS = ['EnterpriseNumber', 'Zipcode', 'MunicipalityFR', 'MunicipalityNL', 'juridicalForm', 'StartingDate','latitudes', 'longitudes', 'provinces', 'Regions', 'Denomination','Description', 'employees']


global dframe
dframe = pd.DataFrame(columns = LABELS)

global state 
state = {
    'filters' : {
        'regions': [],
        'employees': [],
        'jf': []
    },
    'file': [],
    'frame': pd.DataFrame(columns = LABELS)
}

global adQuery
adQuery = None


global filters_regions, filters_employees, filters_JF
filters_regions, filters_employees, filters_JF = build_filters()

#global entities
#entities = get_info(dframe)

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

server = app.server

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
                            options = filters_regions,
                            placeholder="All",
                            multi = True
                        ),

                        html.P('Employees:', style = {'color':'sandybrown','marginLeft':'20px','fontWeight':'bold'}),
                        dcc.Dropdown(
                            id = 'employees',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options = filters_employees,
                            placeholder="All",
                            multi = True
                        ),
                        html.P('Juridical Forms:', style = {'color':'sandybrown','marginLeft':'20px','fontWeight':'bold'}),
                        dcc.Dropdown(
                            id = 'jf',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options = filters_JF,
                            placeholder="All",
                            multi = True
                        ),
                        html.P(),
                        html.P(),
                        html.Button('Search', id='button', style = {'width':'90px', 'height':'30px', 'backgroundColor':'white', 'marginLeft':'20px', 'border':'none', 'backgroundColor':'lightgray', 'color':'white', 'cursor':'pointer'}),

            ],id = "left2")
        
        ])

    ], id = "left"),

    html.Div([

        html.Div(' ', style = {'backgroundColor':'lightgrey', 'height':'50px'}),
        html.Div('Data visualization tools', style = {'color':'mediumvioletred','fontSize':'130%','marginTop':'40px', 'fontWeight':'bold'}),
        html.Div('Select filters aside and make your research from the database. Upload a file if you want to see data from specific enttities.', style = {'color':'gray','fontSize':'90%','marginTop':'40px', 'fontWeight':'bold'}),
        html.P(''),
        html.Hr(style = {'marginLeft':'70px', 'marginRight':'70px', 'color':'lightgray'}),
        html.Div(id = 'empty'),
        html.Div(
            id = 'dataset-info',
            children = [
                html.Div(
                    id = 'update-info'
                )
            ]
            ),
        html.Div(
            id = 'div1',
            children = [
                html.Div(
                    id = 'graph1_container',
                    children = [
                        dcc.Graph(
                            id = 'graph1',
                            figure = create_chart_JF(adQuery)
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            id = 'div2',
            children = [
                html.Div(
                    id = 'graph2_container',
                    children = [
                        dcc.Graph(
                            id = 'graph2',
                            figure = create_chart_age(adQuery)
                        )
                    ],
                ),
            ]
        ),
        html.Div(
            id = 'div3',
            children = [
                html.Div(
                    id = 'graph3_container',
                    children = [
                        dcc.Graph(
                            id = 'graph3',
                            figure = create_chart_starting_date(adQuery)
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            id = 'div4',
            children = [
                html.Div(
                    id = 'graph4_container',
                    children = [
                        dcc.Graph(
                            id = 'graph4',
                            figure = create_chart_employees(adQuery)
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            id = 'div5',
            children = [
                html.Div(
                    id = 'graph5_container',
                    children = [
                        dcc.Graph(
                            id = 'graph5',
                            figure = {
                                'data': [create_chart_mapbox(adQuery)],
                                'layout': DEFAULT_LAYOUT
                            },
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            id = 'div6',
            children = [
                html.Div(
                    id = 'graph6_container',
                    children = [
                        dcc.Graph(
                            id = 'graph6',
                            figure = create_chart_province(adQuery)
                        )
                    ]
                )
            ]
        ),
            
    
        

    ], id = "right")
 
], id = "body_page")

'''
def filter_df(frame, filters={}):
    if 'regions' in filters and filters['regions'] is not None and len(filters['regions']) > 0:
        frame = frame[frame['Regions'].isin(filters.get('regions'))]
    if 'employees' in filters and filters['employees'] is not None and len(filters['employees']) > 0:
        frame = frame[frame['employees'].isin(filters.get('employees'))]
    if 'jf' in filters and filters['jf'] is not None and len(filters['jf']) > 0:
        frame = frame[frame['Description'].isin(filters.get('jf'))]
    
    return frame
'''

@app.callback(
    [Output('div1', 'children'), 
    Output('div2', 'children'),
    Output('div3', 'children'),
    Output('div4', 'children'),
    Output('div5', 'children'),
    Output('div6', 'children'),
    Output('regions', 'options'),
    Output('employees', 'options'),
    Output('jf', 'options'),
    ],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
    State('upload-data', 'last_modified')])
def file_reader(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        for d in children:
            datas = d
        for r in children:
            datas = r

        state['file'] = datas

    else:
        state['file'] = []
    
    adQuery = create_adaptive_query(state)


    return [
            dcc.Graph(
                id = 'graph1',
                figure = create_chart_JF(adQuery)
            )
        ], [
            dcc.Graph(
                id = 'graph2',
                figure = create_chart_age(adQuery)
            )
        ], [
            dcc.Graph(
                id = 'graph3',
                figure = create_chart_starting_date(adQuery)
            )
        ], [
            dcc.Graph(
                id = 'graph4',
                figure = create_chart_employees(adQuery)
            )
        ], [
            dcc.Graph(
                id = 'graph5',
                figure = create_chart_mapbox(adQuery)
            )
        ], [
            dcc.Graph(
                id = 'graph6',
                figure = create_chart_province(adQuery)
            )
        ], filters_regions, filters_employees, filters_JF


'''
@app.callback(
    [Output('graph1_container', 'children'),
    Output('graph2_container', 'children'),
    Output('graph3_container', 'children'),
    Output('graph4_container', 'children'),
    Output('graph5_container', 'children'),
    Output('graph6_container', 'children'),
    Output('dataset-info', 'children')
    ],
    [Input('regions', 'value'),
     Input('employees', 'value'),
     Input('jf', 'value')
     ])
def update_graph(regions, employees, jf):
    
    filters = {
        'regions': regions,
        'employees': employees,
        'jf': jf
    }

    state['filters']['regions'] = regions
    state['filters']['employees'] = employees
    state['filters']['jf'] = jf


    if state['frame'] is not None:
        filtered_df = filter_df(state['frame'].copy(), filters)
        return  create_chart_JF(filtered_df), create_chart_age(filtered_df), create_chart_starting_date(filtered_df), create_chart_employees(filtered_df), create_chart_mapbox(filtered_df), create_chart_province(filtered_df), get_info(filtered_df)
    '''

@app.callback(
    [Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Output('graph3', 'figure'),
    Output('graph4', 'figure'),
    Output('graph5', 'figure'),
    Output('graph6', 'figure'),
    Output('dataset-info', 'children'),
    ],
    [Input('button', 'n_clicks')]
    ,
     [State('regions', 'value'),
     State('employees', 'value'),
     State('jf', 'value')])
def update_from_filters(n_clicks, regions, employees, jf):

    filters = {
        'regions': regions,
        'employees': employees,
        'jf': jf
    }

    state['filters']['regions'] = regions
    state['filters']['employees'] = employees
    state['filters']['jf'] = jf


    adQuery = create_adaptive_query(state)
    return create_chart_JF(adQuery), create_chart_age(adQuery), create_chart_starting_date(adQuery), create_chart_employees(adQuery), create_chart_mapbox(adQuery), create_chart_province(adQuery), get_info(adQuery)


def create_adaptive_query(state):
    filters = state['filters']
    where = ''
    
    regions = []
    employees = []
    jf = []
    numbers = []
    query = ''
    query_filters = []

    if 'regions' in filters and filters['regions'] is not None and len(filters['regions']) > 0:
        regions = filters.get('regions')
        query_filters.append("Regions in ("  + ','.join(['?']*len(regions)) + ")")
    if 'employees' in filters and filters['employees'] is not None and len(filters['employees']) > 0:
        employees = filters.get('employees')
        query_filters.append("employees in (" + ','.join(['?']*len(employees)) + ")")
    if 'jf' in filters and filters['jf'] is not None and len(filters['jf']) > 0:
        jf = filters.get('jf')
        query_filters.append("Description in ("   + ','.join(['?']*len(jf)) + ")")
    if 'file' in state and state['file'] is not None and len(state['file']) > 0:
        numbers=state['file']
        query_filters.append("EnterpriseNumber in ("   + ','.join(['?']*len(state['file'])) + ")")

    
    if len(query_filters) > 0:
        where = " AND ".join(query_filters)
        return AdaptiveQuery(where, parameters=regions+employees+jf+numbers)
    
    return None

if __name__ == '__main__':
    app.run_server(debug=True)
    