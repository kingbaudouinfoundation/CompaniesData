import dash
import base64
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import dash_table
import pandas as pd 
import io
import csv 
import sqlite3

numeros = []

app = dash.Dash(__name__)


app.layout = html.Div([

    html.Div([
        html.Div('Find your information', id = 'top'),

        dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File', style = {'color':'skyblue','textDecoration':'underline'})
        ]),
        style={
            'height': '60px','lineHeight':'60px','borderWidth': '1px','borderStyle': 'dashed','borderRadius': '5px','textAlign': 'center',   
        },
        multiple=True
    ),

    ], id = "header"),
    
    html.Div(id='output-data-upload'),


    html.Div()

    
], id = "body_page")


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    #On récupère les numéros présents dans le csv 
    numeros = df['Ondernemingsnummer'].values

    #On formate les numéros sous la forme 0xxx . xxx . xxx 
    format_numbers = []
    for n in numeros:
        if len(n) == 11:
            s = '0' + '.'.join(n.split())
            format_numbers.append(s)
        #else:
        #   format_numbers.append(n)
 

    ### Connexion à la base de donnée SQLite
    connection = sqlite3.connect('kbo.sqlite3')
    #print('connection Ok')
    statement = connection.cursor()

    fetch_numbers = []

    for n in format_numbers:
        statement.execute("SELECT * FROM enterprise WHERE EnterpriseNumber=:number", {"number": n})
        sql = statement.fetchone()
        if sql != None:
            fetch_numbers.append(sql)
    for line in fetch_numbers:
        print(line)
        

    return html.Div([
        html.Div('Collected data from ' + filename, style = {'padding':'20px','size':'20','fontWeight':'bold','color':'steelblue'}),
        

        #   data=df.to_dict('rows'),
        #   columns=[{'name': i, 'id': i} for i in df.columns]
        #),

    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



if __name__ == '__main__':
    app.run_server(debug=True)