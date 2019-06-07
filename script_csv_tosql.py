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

connection = sqlite3.connect('kbo.sqlite3')
statement = connection.cursor()

df = pd.read_csv('new_table.csv')
df.to_sql(enterprise_details, connection, if_exists='append', index=False)

