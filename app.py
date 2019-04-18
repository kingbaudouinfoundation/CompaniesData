import dash
import base64
import datetime 
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd 
import plotly.plotly as py
import plotly.graph_objs as go
import io
import csv 
import sqlite3

mapbox_access_token = 'pk.eyJ1IjoidGhvbWFzdnJvIiwiYSI6ImNqdWI5Y2JxdjBhYW40NnBpa2RhcHBnb3kifQ.9N4rhGAGmo9zqnXOlt-WOw'

DEFAULT_COLOURS_1 = ['steelblue', 'purple', 'darktruquoise', 'mediumseagreen', 'palegoldenrod', 'lightblue']
DEFAULT_COLOURS_2 = ['indigo', 'gold', 'darkorange']
DEFAULT_COLOURS_3 = ['darkred', 'indianred', 'lemonchiffon', 'lightsalmon', 'orange', 'mediumorchid']

numeros = []

app = dash.Dash(__name__)

app.title = 'Companies Data'

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div(id = 'top'),
            #html.Div('King Baudouin Foundation', id = 'top_bis')
        ], id = "top_page"),

        html.Div([

            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select File', style = {'color':'skyblue','textDecoration':'underline'})
                ], style = {'color':'black'}),
                style={
                    'height': '60px','lineHeight':'60px','textAlign': 'center','backgroundColor':'gainsboro'
                },
                multiple=True
            ),
        ], id = "div_up")

    ], id = "header"),

    html.Div(id='output-data-upload'),


    
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
    df.rename(columns = {'Naam':'Name'}, inplace = True)
    df.rename(columns = {'Ondernemingsnummer':'Entity Number'}, inplace = True)


    #On formate les numéros sous la forme 0xxx . xxx . xxx 
    format_numbers = []
    for n in numeros:
        num = str(n)
        if len(num) == 11:
            s = '0' + '.'.join(n.split())
            format_numbers.append(s)
        #else:
        #   format_numbers.append(n)
 

    ### Connexion à la base de donnée SQLite
    connection = sqlite3.connect('kbo.sqlite3')
    statement = connection.cursor()

    fetch_numbers = []
    data = []

    for n in format_numbers:
        statement.execute("SELECT EntityNumber, JuridicalForm, StartDate, Zipcode, MunicipalityFR, Employees FROM enterprise_addresses WHERE EntityNumber=:number", {"number": n})
        sql = statement.fetchone()
        if sql != None:
            fetch_numbers.append(sql)

    for line in fetch_numbers:
        row = []
        for elt in line:
            row.append(elt)
        data.append(row)
    
    frame = pd.DataFrame(data, columns = ['Entity Number','Juridical Form', 'Start Date', 'ZipCode', 'Municipality', 'Employees'])

    codes = pd.read_sql_query('SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"', connection).rename(columns={'Code': 'Juridical Form'})
    codes['Juridical Form'] = codes['Juridical Form'].astype(float)
    merge = pd.merge(frame, codes, on='Juridical Form')

    geo = pd.read_sql_query('SELECT postcode, city, lat, long, province FROM postcode_geo', connection).rename(columns = {'postcode':'ZipCode'})
    geo['ZipCode'] = geo['ZipCode'].astype(str)
    new_merge1 = pd.merge(merge, geo, on = 'ZipCode')

    names = pd.read_sql_query('SELECT EntityNumber, Denomination FROM denomination WHERE TypeOfDenomination = "001"', connection).rename(columns={'EntityNumber': 'Entity Number'})
    new_merge2 = pd.merge(new_merge1, names, on = 'Entity Number')

    #Constructions des tableaux de données pour les graph

    #Pour le graph des formes juridiques
    all_descriptions = merge.loc[: , "Description"]
    descriptions = []
    descriptions_prop = []

    for d in all_descriptions:
        if descriptions.count(d) == 0:
            descriptions.append(d)
            c = all_descriptions.eq(d).sum()
            descriptions_prop.append(c)
    
    #Histogramme des dates de début des entreprises
    all_dates = merge.loc[: , "Start Date"]
    
    x = []
    year = []
    year_prop = []

    for d in all_dates:
        string = d.split('-')
        new_date = string[2]
        year.append(new_date)

    for d in year:
        if x.count(d) == 0:
            x.append(d)
            c = year.count(d)
            year_prop.append(c)
    
    #Pie chart de l'age des entreprises

    this_year = datetime.datetime.now()
    current_year = int(this_year.year)

    #Calcul de la répartition des tranches d'age
    size = ['1 to 5 year', '5 to 10 year', '10 to 15 year', '15 to 20 year', 'More than 20 year']
    part = []
    C1 = C2 = C3 = C4 = C5 = 0

    count_date = 0
    for d in year:
        if d is not None:
            if current_year - int(d) < 5:
                C1 = C1 + 1
            if current_year - int(d) > 5 and current_year - int(d) < 10:
                C2 = C2 + 1
            if current_year - int(d) > 10 and current_year - int(d) < 15:
                C3 = C3 + 1
            if current_year - int(d) > 15 and current_year - int(d) < 20:
                C4 = C4 + 1
            if current_year - int(d) > 20:
                C5 = C5 + 1
            count_date = count_date + 1
            
    
    part.append(C1)
    part.append(C2)
    part.append(C3)
    part.append(C4)
    part.append(C5)

    #Nombre d'employés
    count_empl = 0
    tab_emp = []
    all_employees = merge.loc[: , "Employees"]
    for e in all_employees:
        if e is not None:
            e = e.replace(' trav.', '')
            e = e.split(' &agrave; ')
            tab_emp.append(e)
            count_empl = count_empl + 1

    empl = ['1 to 5', '5 to 10', '10 to 20', '20 to 50', '50 to 100', '100 to 500', '500 to 1000', 'More than 1000']
    P1 = P2 = P3 = P4 = P5 = P6 = P7 = P8 = 0
    prop_empl = []

    for row in tab_emp:
        if len(row) == 2:
            diff = int(row[1]) - int(row[0])
            if diff <= 5:
                P1 = P1 + 1
            if diff >= 5 and diff <= 10:
                P2 = P2 + 1
            if diff >= 10 and diff <= 20:
                P3 = P3 + 1
            if diff >= 20 and diff <= 50:
                P4 = P4 + 1
            if diff >= 50 and diff <= 100:
                P5 = P5 + 1 
            if diff>= 100 and diff <= 500:
                P6 = P6 + 1
            if diff >= 500 and diff <= 1000:
                P7 = P7 + 1
        if len(row) == 1 and row[0] is not None:
            P8 = P8 + 1
    
    prop_empl.append(P1)
    prop_empl.append(P2)
    prop_empl.append(P3)
    prop_empl.append(P4)
    prop_empl.append(P5)
    prop_empl.append(P6)
    prop_empl.append(P7)
    prop_empl.append(P8)

    #Geolocalisation
    list_lat = []
    list_long = []
    list_name = []
    list_province = []
    prop_province = []
    
    for n in format_numbers:
        temp = new_merge2.loc[new_merge2['Entity Number'] == n]
        rows = temp.values.tolist()
        if len(rows) > 0:
            match = latitue = longitude = avg_lat = avg_long = 0
            prov = ''
            entity_name = ''
            for r in rows: 
                if list_province.count(r[10]) == 0:
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
            

    
    return html.Div([

            html.Div([
                html.P('We found ' + str(len(df.loc[: , "Name"]))+ ' entities in which ' + str(len(format_numbers))+ ' have a correct number')

            ], id = "div_count_entities"),

            html.Div([
                
                dash_table.DataTable(
                    id = 'table',
                    columns = [{'name':i, 'id':i} for i in df.columns],
                    style_cell_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'whitesmoke'
                        }
                    ],
                    style_table = { 'overflowX':'scroll','overflowY': 'scroll','maxHeight':'200'},
                    data = df.to_dict("rows"),
                    style_as_list_view = True,
                    style_cell={'padding': '5px',
                                'maxWidth': 0,
                                'height': 30,
                                'textAlign': 'center'},
                    style_header={
                        'backgroundColor': 'gray',
                        'fontWeight': 'bold',
                        'color': 'white'
                    },
                    n_fixed_rows = 1,
                ),

                dash_table.DataTable(
                    id = 't_merge',
                    columns = [{'name':i, 'id':i} for i in new_merge2.columns],
                    style_cell_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'whitesmoke'
                        }
                    ],
                    style_table = { 'overflowX':'scroll','overflowY': 'scroll','maxHeight':'200'},
                    style_data = {'whitespace':'normal'},
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    data = new_merge2.to_dict("rows"),
                    style_as_list_view = True,
                    style_cell={'padding': '5px',
                                'maxWidth': 0,
                                'height': 30,
                                'textAlign': 'center'},
                    style_header={
                        'backgroundColor': 'gray',
                        'fontWeight': 'bold',
                        'color': 'white'
                    },
                    n_fixed_rows = 1,               
                )

                
            ], id = 'div_table'), 

            

            html.Div([

                html.Div([
                    html.P('Based on ' + str(len(year)) + ' entities')
                ], id = "div_count_age"),

                html.Div([
                    html.P('Based on ' + str(len(all_descriptions)) + ' entities')
                ], id = "div_count_description")

            ], id = "div_first_count_row"),

            html.Div([
                
                html.Div([
                    dcc.Graph(
                    id = "pie_chart_ages",
                    figure = {
                        'data': [
                            go.Pie(
                                labels = size,
                                values = part,
                                hole = .5,
                                marker = {
                                    'colors': DEFAULT_COLOURS_1
                                }
                            )
                        ],
                        'layout': {
                            'title': 'Enterprises age'
                        }
                    }
                ),

                ], id = "div_pie_ages"),
                
                html.Div([
                    dcc.Graph(
                    id = "graph_juridical_form",
                    figure = {  
                       'data': [    
                           go.Pie(
                                labels = descriptions,
                                values = descriptions_prop,
                                hole = .5,
                                marker = {
                                    'colors': DEFAULT_COLOURS_2
                                }
                            )
                        ],
                        'layout': {
                            'title':'Distribution by Juridical Form',
                            
                        }  
                    }
                    ),

                ], id = "div_pie_form"),

                
            ], id = 'first_row'),

            html.Div([

            ], id = "div_second_count_row"),

            html.Div([
                    html.P('Based on ' + str(count_date) + ' entities')
                ], id = "div_count_starting_dates"),

            html.Div([

                html.Div([
                    dcc.Graph(
                        id = "starting_dates",
                        figure = {
                            'data': [
                                go.Bar(
                                    x = x,
                                    y = year_prop,
                                    marker = {
                                        'color':'goldenrod'
                                    }
                                )
                            ],
                            'layout': {
                                'title': 'Starting Dates Histogram',
                                'xaxis':{
                                    'title':'year',
                                    'tickmode':'auto',
                                    'tickandle':'80'
                                },
                                'yaxis':{
                                    'title':'Number of enterprises'
                                }
                            }
                        }
                    ), 
                ], id = "div_bar_dates"),

                
            ], id = "second_row"),

            html.Div([

                    html.Div([
                        html.P('Based on ' + str(count_empl)+ ' entities')
                    ], id = "div_count_empl"),

                    dcc.Graph(
                        id = "graph_employees",
                        figure = {  
                        'data': [    
                            go.Pie(
                                    labels = empl,
                                    values = prop_empl,
                                    hole = 0,
                                    marker = {
                                        'colors': DEFAULT_COLOURS_3
                                    }
                                )
                            ],
                            'layout': {
                                'title':'Number of employees per entity',
                            }  
                        }
                    ),
                ], id = "div_pie_empl"),

            html.Div([
                dcc.Graph(
                    id = "entities_location",
                    figure = {
                        'data': [
                            go.Scattermapbox(
                                lat = list_lat,
                                lon = list_long,
                                mode = 'markers',
                                marker=go.scattermapbox.Marker(
                                    size=9
                                ),
                                text = list_name
                            )
                        ],
                        'layout': LAYOUT_MAPBOX  
                    }
                )
            ], id = "div_map"),

            html.Div([
                html.P('This plot was made using the latitudes and longitudes of the postcodes given in the database. Some entities did not match with any cities and may have been located with an average position (based on ' + str(len(list_lat)) + ' entities).')
            ], id = "text_map")


    ], id = "results")

LAYOUT_MAPBOX = go.Layout(

    title = 'Entities Location',
    mapbox = go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        zoom = 7,
        center=go.layout.mapbox.Center(
            lat = 51.0,
            lon = 4.7
        ),
    ),
    margin = go.layout.Margin(
            l=30,
            r=30,
            b=0,
            t=80,
            pad=0
    ),
)

def show_loader():
    return(html.Div(id = "loader"))

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