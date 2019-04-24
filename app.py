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

mapbox_access_token = 'pk.eyJ1IjoidGhvbWFzdnJvIiwiYSI6ImNqdWI5Y2JxdjBhYW40NnBpa2RhcHBnb3kifQ.9N4rhGAGmo9zqnXOlt-WOw'

DEFAULT_COLOURS_1 = ['maroon', 'coral', 'darktruquoise', 'chocolate', 'palegoldenrod', 'lightblue']
DEFAULT_COLOURS_2 = ['firebrick', 'lightcoral', 'tomato']
DEFAULT_COLOURS_3 = ['darkred', 'indianred', 'lemonchiffon', 'lightsalmon', 'orange', 'mediumorchid']

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
                            id = 'régions',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options=[
                                {'label': 'Flandres', 'value': 'Flandre'},
                                {'label': 'Wallonie', 'value': 'Wallonie'},
                                {'label': 'Bruxelles', 'value': 'Bruxelles'}
                                
                            ],
                            multi = 'True'
                        ),

                        html.P('Size:', style = {'color':'sandybrown','marginLeft':'20px','fontWeight':'bold'}),
                        dcc.Dropdown(
                            id = 'taille',
                            style = {'width':'250px', 'backgroundColor':'white', 'marginLeft':'20px'},
                            options = [
                                {'label':'Small', 'value':'Small'},
                                {'label':'Big', 'value':'Big'},
                                {'label':'Huge', 'value': 'Huge'}
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

    ], id = "right")
 
], id = "body_page")

@cache.memoize(timeout = TIMEOUT)
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

def build_data_starting_date(tab):
    x = []
    year = []
    year_prop = []

    year = [d.split('-')[2] for d in tab]
    x = [d for d in year if x.count(d) == 0]
    year_prop = [year.count(d) for d in year]

    return x, year_prop, year

def build_data_entities_age(tab):
    this_year = datetime.datetime.now()
    current_year = int(this_year.year)
    size = ['1 to 5 year', '5 to 10 year', '10 to 15 year', '15 to 20 year', 'More than 20 year']
    part = []
    C1 = C2 = C3 = C4 = C5 = 0

    count_date = 0
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
            count_date = count_date + 1
            
    part.append(C1)
    part.append(C2)
    part.append(C3)
    part.append(C4)
    part.append(C5)

    return size, part, count_date

def build_data_employees(tab):
    count_empl = 0
    tab_emp = []
    for e in tab:
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
            elif diff >= 5 and diff <= 10:
                P2 = P2 + 1
            elif diff >= 10 and diff <= 20:
                P3 = P3 + 1
            elif diff >= 20 and diff <= 50:
                P4 = P4 + 1 
            elif diff >= 50 and diff <= 100:
                P5 = P5 + 1 
            elif diff>= 100 and diff <= 500:
                P6 = P6 + 1 
            elif diff >= 500 and diff <= 1000:
                P7 = P7 + 1
        elif len(row) == 1 and row[0] is not None:
            P8 = P8 + 1
        
    prop_empl.append(P1)
    prop_empl.append(P2) 
    prop_empl.append(P3)
    prop_empl.append(P4)        
    prop_empl.append(P5)
    prop_empl.append(P6) 
    prop_empl.append(P7)
    prop_empl.append(P8)

    return empl, prop_empl, count_empl

def build_data_geolocation(tab, frame, num):
    list_lat = []
    list_long = []
    list_name = []
    list_province = []
    x_province = []
    y_province = []
    prop_province = []
    list_prop_province = []
    
    for n in num:
        temp = frame.loc[tab == n]
        rows = temp.values.tolist()
        if len(rows) > 0:
            match = latitue = longitude = avg_lat = avg_long = 0
            prov = ''
            entity_name = ''
            for r in rows: 
                if list_province.count(r[10]) == 0:
                    p = [r[10], 0]
                    list_prop_province.append(p)
                    list_province.append(r[10])
                elif r[4] == r[7]:
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
    
    for i in list_prop_province:
        x_province.append(i[0])
        y_province.append(i[1])

    return list_lat, list_long, list_name, x_province, y_province

def create_dict_regions():
    dict_regions = dict()
    dict_regions['Bruxelles (19 communes)'] = 'Bruxelles'
    dict_regions['Brabant Wallon'] = 'Wallonie'
    dict_regions['Brabant Flamand'] = 'Flandre'
    dict_regions['Anvers'] = 'Flandre'
    dict_regions['Limbourg'] = 'Flandre'
    dict_regions['Liège'] = 'Wallonie'
    dict_regions['Namur'] = 'Wallonie'
    dict_regions['Hainaut'] = 'Wallonie'
    dict_regions['Luxembourg'] = 'Wallonie'
    dict_regions['Flandre-Occidentale'] = 'Flandre'
    dict_regions['Flandre-Orientale'] = 'Flandre'

    return dict_regions


@cache.memoize(timeout = TIMEOUT)
def parse_contents(contents, filename, date):

    df = create_dataframe(filename, contents)

    #On récupère les numéros présents dans le csv 
    numeros = []
    numeros = df['Ondernemingsnummer'].values
    df.rename(columns = {'Naam':'Name'}, inplace = True)
    #df.rename(columns = {'Ondernemingsnummer':'Entity Number'}, inplace = True)

    #On formate les numéros sous la forme 0xxx . xxx . xxx 
    format_numbers = ['0' + '.'.join(n.split()) for n in numeros if len(n) == 11]
        
    ### Connexion à la base de donnée SQLite
    connection = sqlite3.connect('kbo.sqlite3')
    statement = connection.cursor()

    query = 'SELECT EntityNumber, JuridicalForm, StartDate, Zipcode, MunicipalityFR, Employees FROM enterprise_addresses WHERE EntityNumber in' + str(tuple(format_numbers))
    frame = pd.read_sql_query(query, connection)

    query = 'SELECT Code, Description from code where Language="FR" and Category="JuridicalForm"'
    codes = pd.read_sql_query(query, connection).rename(columns={'Code': 'JuridicalForm'})
    codes['JuridicalForm'] = codes['JuridicalForm'].astype(float)

    merge = pd.merge(frame, codes, on='JuridicalForm')

    query = 'SELECT postcode, city, lat, long, province FROM postcode_geo'
    geo = pd.read_sql_query(query, connection).rename(columns = {'postcode':'Zipcode'})
    geo['Zipcode'] = geo['Zipcode'].astype(str)

    new_merge = pd.merge(merge, geo, on = 'Zipcode')

    query = 'SELECT EntityNumber, Denomination FROM denomination WHERE TypeOfDenomination = "001"'
    names = pd.read_sql_query(query, connection)

    new_merge = pd.merge(new_merge, names, on = 'EntityNumber')

    #Constructions des tableaux de données pour les graph

    #Pour le graph des formes juridiques
    descriptionsF = merge[['EntityNumber','Description']].groupby('Description').size().to_frame('count')
    
    descriptions = descriptionsF.index.tolist()
    descriptions_prop = descriptionsF.loc[: , 'count']

    
    #Histogramme des dates de début des entreprises
    x, year_prop, year = build_data_starting_date(merge.loc[: , "StartDate"])
    
    #Pie chart de l'age des entreprises
    size, part, count_date = build_data_entities_age(year)
    
    #Nombre d'employés
    empl, prop_empl, count_empl = build_data_employees(merge.loc[: , "Employees"])
    

    #Geolocalisation et répartition par province
    list_lat, list_long, list_name, x_province, y_province = build_data_geolocation(new_merge['EntityNumber'], new_merge, format_numbers)

    #datas pour les filtres
    new_dict = create_dict_regions()
    print(new_dict)


    
    return html.Div([

            html.Div([
                html.P('We found ' + str(len(df.loc[: , "Name"]))+ ' entities in which ' + str(len(format_numbers))+ ' have a correct number')

            ], id = "div_count_entities"),
            

            html.Div([

                 html.Div([
                    dcc.Graph(
                        id = "graph_juridical_form",
                        figure = {  
                        'data': [    
                            go.Bar(
                                    x = descriptions,
                                    y = descriptions_prop,
                                    marker = {
                                        'color': DEFAULT_COLOURS_2
                                    }
                                )
                            ],
                            'layout': {
                                'title':'Distribution by Juridical Form (Based on ' + str(len(merge.loc[:, "Description"])) + ' entities)',
                                
                            }  
                        }
                    ),

                ], id = "div_pie_form"),

                
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
                            'title': 'Enterprises age (Based on ' + str(len(year)) + ' entities)'
                        }
                    }
                ),

                ], id = "div_pie_ages"),
                
               
                
            ], id = 'first_row'),

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
                                'title': 'Starting Dates Histogram (Based on ' + str(count_date) + ' entities)',
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
                                'title':'Number of employees per entity (Based on ' + str(count_empl)+ ' entities)',
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
                                text = list_name,
                                hoverinfo = 'text'
                            )
                        ],
                        'layout': LAYOUT_MAPBOX  
                    }
                )
            ], id = "div_map"),

            html.Div([
                html.P('This plot was made using the latitudes and longitudes of the postcodes given in the database. Some entities did not match with any cities and may have been located with an average position (based on ' + str(len(list_lat)) + ' entities).')
            ], id = "text_map"),

           
                dcc.Graph(
                    id = 'graph_provinces',
                    figure = {
                        'data': [
                            go.Bar (
                                x = y_province,
                                y = x_province,
                                orientation = 'h',
                                marker = {
                                        'color':'purple'
                                    }
                            ) 
                        ],
                        'layout' : LAYOUT_BAR_CHART
                          
                        
                    }
                )


    ], id = "results")

LAYOUT_BAR_CHART = go.Layout(
    title = 'Distribution by province',
    margin = go.layout.Margin(
        b = 100,
        l = 200
    )
       
)

LAYOUT_MAPBOX = go.Layout(

    title = 'Entities Location',
    mapbox = go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        style = 'mapbox://styles/thomasvro/cjuv6sffh09s01foj7rn28quj',
        zoom = 7,
        center=go.layout.mapbox.Center(
            lat = 51.0,
            lon = 4.7
        ),
    ),
    margin = go.layout.Margin(
            l=120,
            r=120,
            b=0,
            t=80,
            pad=0
    ),
)


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