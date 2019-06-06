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

DICT_REGIONS = {
        'Bruxelles' : 'Bruxelles (19 communes)',
        'Wallonie' : ['Brabant Wallon', 'Liège', 'Namur', 'Hainaut', 'Luxembourg'],
        'Flandre' : ['Brabant Flamand', 'Anvers', 'Limbourg', 'Flandre-Occidentale', 'Flandre-Orientale']
}


#
# get_info : takes a dataframe and returns an Html component to display the frame's information 
#
# Params:
# @frame : frame created from the csv file
def get_info(adQuery = None):

    if adQuery is None:
        return html.Div([
                    html.Div('We found', style = {'marginTop':'50px','fontSize':'140%', 'color':'darkgray','fontWeight':'bold'}),
                    html.Br(),
                    html.Div([
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div('0', style = {'fontSize':'350%'}),
                            html.Div('entities'), 
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'lightskyblue','borderRadius':'50%'}),
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div('0', style = {'fontSize':'350%'}),
                            html.Div('y.o middle-aged'), 
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'goldenrod','borderRadius':'50%'}),
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div('over'),
                            html.Div('0', style = {'fontSize':'250%'}),
                            html.Div('employees')
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'purple','borderRadius':'50%'}),
                    ], style = {'textAlign':'center'}),
                    
                ], style = {'textAlign':'center', 'alignItems':'center', 'justifyContent':'center'})

    
    
    else:

        entities = str(adQuery.count())
        dates = [int(d) for d in adQuery.get('StartingDate')]
        employees = [e for e in adQuery.get('employees')]
        
        inf = 0
        c = 0
        for e in employees:
            x = e.split(' to ')
            if len(x) > 1:
                i = int(x[0])
                j = int(x[1])
                inf = inf + i
            if len(x) == 0 and x is not None:
                inf = inf + 1000

        this_year = datetime.datetime.now()
        current_year = int(this_year.year)
        s = (sum(dates))
        
        if len(dates) == 0:
            x = 0
        else:
            x = s / len(dates)

        avg_age = round(current_year - x)

        return html.Div([
                    html.Div('We found', style = {'marginTop':'50px','fontSize':'140%', 'color':'darkgray','fontWeight':'bold'}),
                    html.Br(),
                    html.Div([
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div(entities, style = {'fontSize':'350%'}),
                            html.Div('entities'), 
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'lightskyblue','borderRadius':'50%'}),
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div(str(avg_age), style = {'fontSize':'350%'}),
                            html.Div('y.o middle-aged'), 
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'goldenrod','borderRadius':'50%'}),
                        html.Span([
                            html.Br(),
                            html.Br(),
                            html.Div('over'),
                            html.Div(str(inf), style = {'fontSize':'250%'}),
                            html.Div('employees')
                        ],style = {'height':'150px', 'width':'150px','display':'inline-block','color':'white','backgroundColor':'purple','borderRadius':'50%'}),
                    ], style = {'textAlign':'center'}),
                    
                ], style = {'textAlign':'center', 'alignItems':'center', 'justifyContent':'center'})

#
# build_filters : takes a dataframe and changes the filters value in function of the dataframe
#                 returns 3 lists containing the right values 
#
# Params:
# @frame : the dataframe with which the filters value are created
def build_filters():

    connection = sqlite3.connect('kbo.sqlite3')
    statement = connection.cursor()

    query_regions = 'SELECT DISTINCT Regions from enterprises_addresses'
    get_regions = pd.read_sql_query(query_regions, connection)
    list_regions = get_regions.loc[: , 'Regions']
    filters_regions = []
    for r in list_regions:
        filters_regions.append({'label': r, 'value': r})
    
    query_employees = 'SELECT DISTINCT employees from enterprises_addresses'
    get_employees = pd.read_sql_query(query_employees, connection)
    list_employees = get_employees.loc[: , 'employees']
    filters_employees = []
    for r in list_employees:
        filters_employees.append({'label': r, 'value': r})
    
    query_descriptions = 'SELECT DISTINCT Description from enterprises_addresses'
    get_descriptions = pd.read_sql_query(query_descriptions, connection)
    list_descriptions = get_descriptions.loc[: , 'Description']
    filters_JF = []
    for r in list_descriptions:
        filters_JF.append({'label': r, 'value': r})
    
    return filters_regions, filters_employees, filters_JF

#
# create_dataframe : takes a name and a value to convert a csv file to a dataframe
#
# Params:
# @name: the csv file's name
# @content: the content of the csv file
def create_dataframe(name, contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in name:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            return df
        elif 'xls' in name:
            df = pd.read_excel(io.BytesIO(decoded))
            return df
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

#
# get_datas_starting_dates : takes a list 
#                            returns two lists (x and year_prop) to build the chart of entities starting dates
#
# Params:
# @tab: the list containing all the starting dates in the dataframe
def get_datas_starting_date(tab):
    x = []
    year = []
    year_prop = []

    year = [d for d in tab]
    x = [d for d in year if x.count(d) == 0]
    year_prop = [year.count(d) for d in year]

    return x, year_prop

#
# get_datas_entities_age : takes a list
#                          returns a list (part) which contains every proportion of each slice of age
#
# Params:
# @tab : the list containing the starting dates of the entities
def get_datas_entities_age(tab):
    this_year = datetime.datetime.now()
    current_year = int(this_year.year)
    part = []
    C1 = C2 = C3 = C4 = C5 = 0

    for d in tab:
        if d is not None:
            if current_year - int(d) < 5:
                C1 = C1 + 1
            elif current_year - int(d) > 5 and current_year - int(d) < 10:
                C2 = C2 + 1
            elif current_year - int(d) > 10 and current_year - int(d) < 15:
                C3 = C3 + 1
            elif current_year - int(d) > 15 and current_year - int(d) < 20:
                C4 = C4 + 1
            elif current_year - int(d) > 20:
                C5 = C5 + 1
           
    part.append(C1)
    part.append(C2)
    part.append(C3)
    part.append(C4)
    part.append(C5)

    return part

#
# format_employees : takes a list, returns a new list. Format the employees column from ' x &agrave x ' to ' x to x '
#
# Params:
# @tab : the list containing the values of employees
def format_employees(tab):
    tab_emp = []
    for e in tab:
        if e is not None:
            e = e.replace(' trav.', '')
            e = e.split(' &agrave; ')
            e = ' to '.join(e)
            tab_emp.append(str(e))
    
    return tab_emp
    
#
# get_datas_employees : takes a list, returns two list (prop_emp, list_emp) to create the chart of employees number
#                       
# Params:
# @tab: the list containing the values of employees
def get_datas_employees(tab):

    P1 = P2 = P3 = P4 = P5 = P6 = P7 = P8 = P9 = 0
    list_emp = []
    prop_empl = []
    for row in tab:
        if ' to ' in row:
            x = row.split(' to ')
            #diff = int(x[1]) - int(x[0])
            if int(x[0]) <= 5:
                P1 = P1 + 1
                list_emp.append('1 to 5')          
            elif int(x[0]) >= 5 and int(x[1]) <= 10:
                P2 = P2 + 1
                list_emp.append('5 to 10')
            elif int(x[0]) >= 10 and int(x[1]) <= 20:
                P3 = P3 + 1
                list_emp.append('10 to 20')
            elif int(x[0]) >= 20 and int(x[1]) <= 50:
                P4 = P4 + 1
                list_emp.append('20 to 50')             
            elif int(x[0]) >= 50 and int(x[1]) <= 100:
                P5 = P5 + 1 
                list_emp.append('50 to 100')
            elif int(x[0]) >= 100 and int(x[1]) <= 500:
                P6 = P6 + 1 
                list_emp.append('100 to 500')
            elif int(x[0]) >= 500 and int(x[1]) <= 1000:
                P7 = P7 + 1
                list_emp.append('500 to 1000')
        elif 'more than 1000' in row:
            P8 = P8 + 1
            list_emp.append('More than 1000')
        elif row == '0':
            P9 = P9 + 1
            list_emp.append('0')
        
    prop_empl.append(P1)
    prop_empl.append(P2) 
    prop_empl.append(P3)
    prop_empl.append(P4)        
    prop_empl.append(P5)
    prop_empl.append(P6) 
    prop_empl.append(P7)
    prop_empl.append(P8)
    prop_empl.append(P9)

    return prop_empl, list_emp


def parse_contents(contents, filename, date):

    df = create_dataframe(filename, contents)
    numeros = []
    numeros = df['Ondernemingsnummer'].values

    format_numbers = ['0' + '.'.join(n.split()) for n in numeros if len(n) == 11]
    
    return format_numbers

class AdaptiveQuery:
    
    def __init__(self, where, parameters=(), db_name='/Users/Thomas/Documents/Fondation/Python/CompaniesData/kbo.sqlite3', table='enterprises_addresses', threshold=1000):
        self.where = where
        self.parameters = parameters
        self.db_name = db_name
        self.table = table
        self.df = None
        
        if self.count() < threshold:
            self.get_df()
    
    '''
    create and save in self.df a dataframe based on the where clause
    '''
    def get_df(self):
        with sqlite3.connect(self.db_name) as con:
            self.df = pd.read_sql('SELECT * FROM '+self.table+' WHERE '+self.where, params=self.parameters, con=con)
    
    '''
    Perform a SQL query
    '''
    def query(self, fields='*', extra=''):
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            query = 'SELECT '+ fields+' FROM '+self.table+' WHERE '+self.where+' '+extra
            return cur.execute(query, self.parameters).fetchall()
    
    '''
    perform a group by on a column or list of columns
    '''
    def groupby_count(self, columns):
        if self.df is not None:
            return self.df.groupby(columns).size().to_frame('count').reset_index(columns).values.tolist()
        else:
            if not isinstance(columns, str):
                columns = ','.join(columns)
            return self.query(fields = columns + ', count(*)', extra='GROUP BY '+columns)
    
    
    '''
    columns is either a column name or a list of column names
    '''
    def get(self, columns):
        if self.df is not None:
            return self.df[columns].values.tolist()
        else:
            if not isinstance(columns, str):
                columns = ','.join(columns)
            val = self.query(fields = columns)
        
            if isinstance(columns, str):
                return [x[0] for x in val]
            else:
                return val
        
    '''
    return the number of rows selected by the where clause
    '''
    def count(self):
        if self.df is not None:
            return self.df.shape[0]
        else:
            return self.query(fields = 'count(*)')[0][0]