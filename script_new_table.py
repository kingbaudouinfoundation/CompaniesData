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

query = 'SELECT EntityNumber, JuridicalForm, StartDate, Zipcode, MunicipalityFR, MunicipalityNL, Employees FROM enterprise_addresses WHERE Zipcode IS NOT NULL AND MunicipalityFR IS NOT NULL'
main_frame = pd.read_sql_query(query, connection)

query = 'SELECT postcode, LOWER(city) AS city, long, lat, province FROM postcode_geo'
frame = pd.read_sql_query(query, connection)

dict_cities = {}

for row in frame.iterrows():
    dict_cities[str(row[1]['postcode']) + ' - ' + row[1]['city']] = row[1]

latitude = []
longitude = []
province = []
wrong = []
count = 0

data = []

timer1 = datetime.datetime.now()
print('')
print('Processing...')
print('')
for enterprise in main_frame.iterrows():
        fr_key = enterprise[1]['Zipcode'] + ' - ' + enterprise[1]['MunicipalityFR'].lower()
        nl_key = enterprise[1]['Zipcode'] + ' - ' + enterprise[1]['MunicipalityNL'].lower()
        if fr_key in dict_cities:
                x = dict_cities.get(fr_key)
                y = enterprise[1].tolist()
                y.append(x['lat'])
                y.append(x['long'])
                y.append(x['province'])
                data.append(y)
                
        elif nl_key in dict_cities:
                x = dict_cities.get(fr_key)
                y = enterprise[1].tolist()
                y.append(x['lat'])
                y.append(x['long'])
                y.append(x['province'])
                data.append(y)

        else:
                count = count + 1
                y = enterprise[1].tolist()
                query = "SELECT long, lat, province FROM postcode_geo WHERE postcode = '" + enterprise[1]['Zipcode'] + "'"
                temp = pd.read_sql_query(query, connection)
                if len(temp) > 0:
                        s_lat = 0
                        s_long = 0
                        for row in temp.iterrows():
                                s_lat = s_lat + float(row[1]['lat'])
                                s_long = s_long + float(row[1]['long'])
                        avg_lat = s_lat / len(temp)
                        avg_long = s_long / len(temp)
                        y.append(avg_lat)
                        y.append(avg_long)
                        y.append(row[1]['province'])
               
                
timer2 = datetime.datetime.now()

LABELS = ['EntityNumber', 'JuridicalForm', 'StartDate', 'Zipcode', 'MunicipalityFR', 'MunicipalityNL', 'Employees','latitude', 'longitude', 'province']
dframe = pd.DataFrame(data, columns = LABELS)

tab_emp = format_employees(dframe.loc[: , "Employees"])
prop_empl, list_emp = get_datas_employees(tab_emp)
dframe['employees'] = list_emp
dframe.drop('Employees', axis = 1, inplace = True)

tab_year =[d.split('-')[2] for d in dframe.loc[: , 'StartDate']]
dframe['StartingDate'] = tab_year
dframe.drop('StartDate', axis = 1, inplace = True)

query = 'SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"'
codes = pd.read_sql_query(query, connection).rename(columns={'Code': 'JuridicalForm'})
codes['JuridicalForm'] = codes['JuridicalForm'].astype(float)

dframe = pd.merge(dframe, codes, on = 'JuridicalForm')

query = 'SELECT EntityNumber, Denomination FROM denomination WHERE TypeOfDenomination = "001"'
names = pd.read_sql_query(query, connection)

dframe = pd.merge(dframe, names, on = 'EntityNumber')

list_regions = []
for p in dframe.loc[: , 'province']:
        if p in DICT_REGIONS.get('Bruxelles'):
                list_regions.append('Bruxelles')
        elif p in DICT_REGIONS.get('Wallonie'):
                list_regions.append('Wallonie')
        elif p in DICT_REGIONS.get('Flandre'):
                list_regions.append('Flandre')

dframe['Regions'] = list_regions

dframe.to_csv('new_table.csv', index = False)

print(count)
print('dataframe created: ' + str(len(data)) + ' rows')
marker = timer2 - timer1
print(" ")
print("duration: " + str(marker))
print(" ")



connection.close()