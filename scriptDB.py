import pandas as pd 
import base64
import csv 
import sqlite3
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import io

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
            'height': '60px','lineHeight':'60px','borderWidth': '1px','borderStyle': 'dashed','borderRadius': '5px','textAlign': 'center','backgroundColor':'white' 
        },
        multiple=True
    ),

    ], id = "header"),
    
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), low_memory = False)
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded), low_memory = False)
    except Exception as e:
        print(e)
        return("error while processing the file")

    connection = sqlite3.connect('kbo.sqlite3')

    df.to_sql('enterprise_addresses', connection)

    max_rows = 10

    return html.Div([

        html.Table(
                
            [html.Tr([html.Th(col) for col in df.columns]) ] +
                
            [html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))]
        ),

        html.Div()

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