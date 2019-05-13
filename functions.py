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
def get_info(frame):

    if frame is None or len(frame) == 0:
        return html.Div('')

    entities = str(len(frame))
    dates = [int(d.split('-')[2]) for d in frame.loc[: , 'StartDate']]
    employees = [e for e in frame.loc[: , 'employees']]
    
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
    
    if frame is not None:
        this_year = datetime.datetime.now()
        current_year = int(this_year.year)
        s = (sum(dates))
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
def build_filters(frame):
    get_regions = frame[['EntityNumber','Regions']].groupby('Regions').size().to_frame('count')
    list_regions = get_regions.index.tolist()
    filters_regions = []
    for r in list_regions:
        filters_regions.append({'label': r, 'value': r})
    
    get_employees = frame[['EntityNumber','employees']].groupby('employees').size().to_frame('count')
    list_employees = get_employees.index.tolist()
    filters_employees = []
    for e in list_employees:
        filters_employees.append({'label': e, 'value': e})
    
    get_JF = frame[['EntityNumber','Description']].groupby('Description').size().to_frame('count')
    list_JF = get_JF.index.tolist()
    filters_JF = []
    for jf in list_JF:
        filters_JF.append({'label': jf, 'value': jf})
    
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

    year = [d.split('-')[2] for d in tab]
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
        else:
            tab_emp.append('Unkwown')
    
    return tab_emp
    
#
# get_datas_employees : takes a list, returns two list (prop_emp, list_emp) to create the chart of employees number
#                       
# Params:
# @tab: the list containing the values of employees
def get_datas_employees(tab):

    P1 = P2 = P3 = P4 = P5 = P6 = P7 = P8 = 0
    list_emp = []
    prop_empl = []
    for row in tab:
        x = row.split(' to ')
        if x is None:
            list_emp.append('Unkwown')
        if len(x) > 1:
            diff = int(x[1]) - int(x[0])
            if diff <= 5:
                P1 = P1 + 1
                list_emp.append('1 to 5')          
            elif diff >= 5 and diff <= 10:
                P2 = P2 + 1
                list_emp.append('5 to 10')
            elif diff >= 10 and diff <= 20:
                P3 = P3 + 1
                list_emp.append('10 to 20')
            elif diff >= 20 and diff <= 50:
                P4 = P4 + 1
                list_emp.append('20 to 50')             
            elif diff >= 50 and diff <= 100:
                P5 = P5 + 1 
                list_emp.append('50 to 100')
            elif diff>= 100 and diff <= 500:
                P6 = P6 + 1 
                list_emp.append('100 to 500')
            elif diff >= 500 and diff <= 1000:
                P7 = P7 + 1
                list_emp.append('500 to 1000')
        elif tab is not None:
            P8 = P8 + 1
            list_emp.append('More than 1000')
        
    prop_empl.append(P1)
    prop_empl.append(P2) 
    prop_empl.append(P3)
    prop_empl.append(P4)        
    prop_empl.append(P5)
    prop_empl.append(P6) 
    prop_empl.append(P7)
    prop_empl.append(P8)

    return prop_empl, list_emp

def build_data_geolocation(tab, frame, num):
    list_lat = []
    list_long = []
    list_name = []
    list_province = []
    provinces = []
    x_province = []
    y_province = []
    prop_province = []
    list_prop_province = []
    
    for n in num:
        temp = frame.loc[tab == n]
        rows = temp.values.tolist()
        if len(rows) == 0:
            print(n)
        if len(rows) > 0 and len(rows) is not None:
            match = latitude = longitude = avg_lat = avg_long = 0
            prov = ''
            entity_name = ''
            for r in rows: 
                if list_province.count(r[10]) == 0 and r[10] is not None:
                    p = [r[10], 0]
                    list_prop_province.append(p)
                    list_province.append(r[10])
                if r[4] == r[7]:
                    latitude = r[8]
                    longitude = r[9]
                    entity_name = r[11]
                    match = 1
                else:
                    avg_lat = avg_lat + float(r[8])
                    avg_long = avg_long + float(r[9])
                    entity_name = r[11]
                    match = match
            if match == 1:
                list_lat.append(latitude)
                list_long.append(longitude)
                list_name.append(entity_name)
            else:
                list_lat.append(avg_lat / len(temp.loc[: , 'city']))
                list_long.append(avg_long / len(temp.loc[: , 'city']))
                list_name.append(entity_name)
            line = rows[0]
            for i in list_prop_province:
                if line[10] == i[0]:
                    i[1] = i[1] + 1
                    provinces.append(line[10])
                
    for i in list_prop_province:
        x_province.append(i[0])
        y_province.append(i[1])

    return list_lat, list_long, list_name, x_province, y_province, provinces

def parse_contents(contents, filename, date):

    timer1 = datetime.datetime.now()
    df = create_dataframe(filename, contents)
    timer2 = datetime.datetime.now()

    marker1 = timer2 - timer1
    print(" ")
    print("Dataframe parsing: ")
    print("begin at: " + str(timer1))
    print("ends at: " + str(timer2))
    print("duration: " + str(marker1))
    print(" ")


    numeros = []
    numeros = df['Ondernemingsnummer'].values

    format_numbers = ['0' + '.'.join(n.split()) for n in numeros if len(n) == 11]
    
    connection = sqlite3.connect('kbo.sqlite3')
    statement = connection.cursor()

    
    timer3 = datetime.datetime.now()
    query = 'SELECT EntityNumber, JuridicalForm, StartDate, Zipcode, MunicipalityFR, Employees FROM enterprise_addresses WHERE EntityNumber in' + str(tuple(format_numbers)) + 'AND Zipcode IS NOT NULL AND MunicipalityFR IS NOT NULL'
    frame = pd.read_sql_query(query, connection)
    timer4 = datetime.datetime.now()

    marker2 = timer4 - timer3
    print(" ")
    print("fetchind datas with DB: ")
    print("begin at: " + str(timer3))
    print("ends at: " + str(timer4))
    print("duration: " + str(marker2))
    print(" ")

    
    timer5 = datetime.datetime.now()
    query = 'SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"'
    codes = pd.read_sql_query(query, connection).rename(columns={'Code': 'JuridicalForm'})
    codes['JuridicalForm'] = codes['JuridicalForm'].astype(float)

    merge = pd.merge(frame, codes, on='JuridicalForm')
    timer6 = datetime.datetime.now()

    marker3 = timer6 - timer5
    print(" ")
    print("merging with dataframe code: ")
    print("begin at: " + str(timer5))
    print("ends at: " + str(timer6))
    print("duration: " + str(marker3))
    print(" ")


    timer7 = datetime.datetime.now()
    query = 'SELECT postcode, city, lat, long, province FROM postcode_geo'
    geo = pd.read_sql_query(query, connection).rename(columns = {'postcode':'Zipcode'})
    geo['Zipcode'] = geo['Zipcode'].astype(str)

    new_merge = pd.merge(merge, geo, on = 'Zipcode')
    timer8 = datetime.datetime.now()

    marker4 = timer8 - timer7
    print(" ")
    print("merging with dataframe postcode_geo: ")
    print("begin at: " + str(timer7))
    print("ends at: " + str(timer8))
    print("duration: " + str(marker4))
    print(" ")

    timer9 = datetime.datetime.now()
    query = 'SELECT EntityNumber, Denomination FROM denomination WHERE EntityNumber in' + str(tuple(format_numbers)) + 'AND TypeOfDenomination = "001"'
    names = pd.read_sql_query(query, connection)
    timer10 = datetime.datetime.now()

    connection.close()

    new_merge = pd.merge(new_merge, names, on = 'EntityNumber')
    
    marker5 = timer10 - timer9
    print(" ")
    print("merging with dataframe denomination: ")
    print("begin at: " + str(timer9))
    print("ends at: " + str(timer10))
    print("duration: " + str(marker5))
    print(" ")

    timer11 = datetime.datetime.now()
    tab_emp = format_employees(merge.loc[: , "Employees"])
    prop_empl, list_emp = get_datas_employees(tab_emp)
    merge['employees'] = list_emp
    merge.drop('Employees', axis = 1, inplace = True)

    list_lat, list_long, list_name, x_province, y_province, provinces = build_data_geolocation(new_merge['EntityNumber'], new_merge, merge.loc[: , 'EntityNumber'])
    merge['latitude'] = list_lat
    merge['longitude'] = list_long
    merge['province'] = provinces

    list_regions = []
    for p in merge.loc[: , 'province']:
        if p in DICT_REGIONS.get('Bruxelles'):
            list_regions.append('Bruxelles')
        elif p in DICT_REGIONS.get('Wallonie'):
            list_regions.append('Wallonie')
        elif p in DICT_REGIONS.get('Flandre'):
            list_regions.append('Flandre')
    
    merge['Regions'] = list_regions
    merge['Denomination'] = new_merge.loc[: , 'Denomination']
    timer12 = datetime.datetime.now()

    marker6 = timer12 - timer11
    print(" ")
    print("Removing useless rows in dataframe: ")
    print("begin at: " + str(timer11))
    print("ends at: " + str(timer12))
    print("duration: " + str(marker6))
    print(" ")


    
    return merge.values.tolist()