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

from functions import format_employees, get_datas_employees

DICT_REGIONS = {
        'Bruxelles' : 'Bruxelles (19 communes)',
        'Wallonie' : ['Brabant Wallon', 'Liège', 'Namur', 'Hainaut', 'Luxembourg'],
        'Flandre' : ['Brabant Flamand', 'Anvers', 'Limbourg', 'Flandre-Occidentale', 'Flandre-Orientale']
}

connection = sqlite3.connect('kbo.sqlite3')
statement = connection.cursor()

'''
list_jf = []
query = 'SELECT EntityNumber, JuridicalForm, StartDate, Zipcode, MunicipalityFR, MunicipalityNL FROM enterprise_addresses'
frame1 = pd.read_sql_query(query, connection).rename(columns={'EntityNumber': 'EnterpriseNumber'})
for jf in frame1.loc[: , 'JuridicalForm']:
    jf = str(jf)
    if jf == 'nan':
        jf = ''
        list_jf.append(jf)
    else:
        jf = jf.split('.')
        jf = jf[0]
        list_jf.append(jf)

frame1['juridicalForm'] = list_jf
frame1.drop('JuridicalForm', axis = 1, inplace = True)

query = 'SELECT EnterpriseNumber, Employees from employees'
frame2 = pd.read_sql_query(query, connection)

merge = pd.merge(frame1, frame2, on = 'EnterpriseNumber')
'''

'''
query = 'SELECT * from enterprises_addresses'
frame1 = pd.read_sql_query(query, connection)

query = 'SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"'
frame2 = pd.read_sql_query(query, connection).rename(columns={'Code': 'juridicalForm'})

merge = pd.merge(frame1, frame2, how = 'left', on = 'juridicalForm')
merge.to_csv('enterprise_addresses.csv', index = False)
'''

'''
query = 'SELECT * from enterprises_addresses'
frame1 = pd.read_sql_query(query, connection)
tab_year =[d.split('-')[2] for d in frame1.loc[: , 'StartDate']]
frame1['StartingDate'] = tab_year
frame1.drop('StartDate', axis = 1, inplace = True)


frame1.to_csv('enterprise_addresses.csv', index = False)
'''
'''
query = 'SELECT * from enterprises_addresses'
frame1 = pd.read_sql_query(query, connection)

query = 'SELECT postcode, LOWER(city) AS city, long, lat, province FROM postcode_geo'
frame = pd.read_sql_query(query, connection)

dict_cities = {}

for row in frame.iterrows():
    dict_cities[str(row[1]['postcode']) + ' - ' + row[1]['city']] = row[1]

latitudes = []
longitudes = []
provinces = []

for row in frame1.iterrows():
    fr_key = row[1]['Zipcode'] + ' - ' + row[1]['MunicipalityFR'].lower()
    nl_key = row[1]['Zipcode'] + ' - ' + row[1]['MunicipalityNL'].lower()
    if fr_key in dict_cities:
        match = dict_cities.get(fr_key)
        latitudes.append(match['lat'])
        longitudes.append(match['long'])
        provinces.append(match['province'])
    elif nl_key in dict_cities:
        match = dict_cities.get(nl_key)
        latitudes.append(match['lat'])
        longitudes.append(match['long'])
        provinces.append(match['province'])
    elif row[1]['Zipcode'] == '' or row[1]['Zipcode'] + ' - ' + row[1]['MunicipalityFR'].lower() not in dict_cities or row[1]['Zipcode'] + ' - ' + row[1]['MunicipalityNL'].lower() not in dict_cities:
        latitudes.append('')
        longitudes.append('')
        provinces.append('')

frame1['latitudes'] = latitudes
frame1['longitudes'] = longitudes
frame1['provinces'] = provinces 

regions = []
for p in frame1.loc[: , 'provinces']:
        if p in DICT_REGIONS.get('Bruxelles'):
                regions.append('Bruxelles')
        elif p in DICT_REGIONS.get('Wallonie'):
                regions.append('Wallonie')
        elif p in DICT_REGIONS.get('Flandre'):
                regions.append('Flandre')

frame1['Regions'] = regions
'''
'''
query = 'SELECT * from enterprises_addresses'
frame1 = pd.read_sql_query(query, connection)

query = 'SELECT EntityNumber, Denomination FROM denomination WHERE Language = 1 and TypeOfDenomination = "001"'
frame2 = pd.read_sql_query(query, connection).rename(columns={'EntityNumber': 'EnterpriseNumber'})

merge = pd.merge(frame1, frame2, how = 'left', on = 'EnterpriseNumber')
'''
'''
query = 'SELECT * from enterprises_addresses'
frame1 = pd.read_sql_query(query, connection)
query = 'SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"'
frame2 = pd.read_sql_query(query, connection).rename(columns={'Code': 'juridicalForm'})
merge = pd.merge(frame1, frame2, how = 'left', on = 'juridicalForm')

merge.to_csv('enterprises_addresses.csv', index = False)
'''
query = 'SELECT * from enterprises_addreses'
frame = pd.read_sql_query(query, connection)

p, l = get_datas_employees(frame.loc[: , 'Employees'])
frame['employees'] = l
frame.drop('Employees', axis = 1, inplace = True)

frame.to_csv('enterprises_addresses', index = False)