import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot, plot
import cufflinks as cf
import requests
import dash
import dash_html_components as html
import dash_core_components as dcc
import re


# import plotly.graph_objects as go
# UPDADE_INTERVAL = 300
init_notebook_mode(connected=True)
sns.set(style="whitegrid")

global totalCases
global totalDeaths
global totalRecovered
global activeCases
global choromap
global fig


def get_new_data():
    global fig
    global totalCases
    global totalDeaths
    global totalRecovered
    global activeCases
    global choromap
    global country
    global ttlCases
    global ttlRec

    html_source1 = requests.get("https://www.worldometers.info/coronavirus/").text
    html_source1 = re.sub(r'<.*?>', lambda g: g.group(0).upper(), html_source1)
    df1 = pd.read_html(html_source1)

    html_source2 = requests.get("https://www.worldometers.info/coronavirus/coronavirus-death-toll").text
    html_source2 = re.sub(r'<.*?>', lambda g: g.group(0).upper(), html_source2)
    df2 = pd.read_html(html_source2)

    covdf = df1[0]
    # Remove last row (Total)
    covdf.drop(covdf.head(1).index, inplace=True)
    covdf.drop(covdf.tail(1).index, inplace=True)
    dailydeaths = df2[0]
    covdf = covdf.replace(np.nan, 0)
    covdf['text'] = covdf[
        ['Country,Other', 'TotalCases', 'ActiveCases', 'TotalDeaths', 'TotalRecovered', 'NewCases']].apply(impute_text,
                                                                                                           axis=1)
    last20dailydeaths = dailydeaths.head(20)
    x = last20dailydeaths['Date']
    y = last20dailydeaths['Total Deaths']
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    fig.update_layout(title='Deaths in Last 20 Days',
                      xaxis_title='Date',
                      yaxis_title='Novel Coronavirus Daily Deaths',
                      width=348,
                      height=400,
                      margin=dict(l=20, r=20, t=25, b=20))

    worldmap = dict(
        type='choropleth',
        colorscale='portland',
        reversescale=True,
        # showscale = False,
        locations=covdf['Country,Other'],
        locationmode="country names",
        z=covdf['TotalCases'],
        text=covdf['text'],
        hovertemplate='<b>%{text}</b>',
        hoverlabel={
            "namelength": 0},
        # marker = dict(line = dict(color = 'rgb(255,255,255)',width = 1)),
        colorbar={'title': ' '},
    )

    layout = dict(title='Hover over a country or territory to see more details', autosize=True,
                  geo=dict(showframe=False, showlakes=True,
                           lakecolor='rgb(85,173,240)', projection={'type': 'natural earth'})
                  )
    choromap = go.Figure(data=worldmap, layout=layout)

    ttlCases = covdf['TotalCases']
    ttlRec = covdf['TotalRecovered']
    country = covdf['Country,Other']
    # Sum rows and format final value
    totalCases = covdf['TotalCases'].sum()
    totalCases = format(totalCases, ",d")
    # converting float numbers to integer with int()
    totalDeaths = int(covdf['TotalDeaths'].sum())
    totalDeaths = format(totalDeaths, ",d")
    totalRecovered = int(covdf['TotalRecovered'].sum())
    totalRecovered = format(totalRecovered, ",d")
    activeCases = int(covdf['ActiveCases'].sum())
    activeCases = format(activeCases, ",d")


# def get_new_data_every(period=UPDADE_INTERVAL):
#    """Update the data every 'period' seconds"""
#    while True:
#       get_new_data()
##       time.sleep(period)


def impute_text(cols):
    country = cols[0]
    total = cols[1]
    active = cols[2]
    deaths = cols[3]
    recovered = cols[4]
    new = cols[5]

    text = str(country) + '<br>' + '<br>' + 'Total: ' + str(total) + '<br>' + 'Active Cases: ' + str(
        active) + '<br>' + 'Dead: ' + str(deaths) + '<br>' + 'Recovered: ' + str(
        recovered) + '<br>' + 'Today cases: ' + str(new)
    return text


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
                )
server = app.server

get_new_data()

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Header('Data Analysis By Chepelesu Kaunda Email:chepekaunda01@gmail.com',
                        style={'text-align': 'right', 'color': '#000000', 'font-size': 12, 'font-weight': 'bold'}),
        ])
    ]),
    html.Div([
        html.H2('Coronavirus COVID-19 Global Cases', style={'text-align': 'center'}),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='g0', figure=fig)
        ], className="three columns"),
        html.Div([
            dcc.Graph(id='g1', figure=choromap)
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='g2',
                      figure={
                          'data': [
                              dict(
                                  x=ttlCases,
                                  y=ttlRec,
                                  text=country,
                                  mode='markers',
                                  opacity=0.7,
                                  marker={
                                      'size': 15,
                                      'line': {'width': 0.5, 'color': 'white'}
                                  },
                              )
                          ],
                          'layout': dict(
                              title='Total Reported/Recovered Cases',
                              xaxis={'type': 'log', 'title': 'Total Reported Cases'},
                              yaxis={'title': 'No. of Recovered Patients'},
                              width=300,
                              height=400,
                              margin={'l': 40, 'b': 40, 't': 25, 'r': 25},
                              legend={'x': 0, 'y': 1},
                              hovermode='closest'
                          )

                      })
        ], className="three columns")
    ], className="row"),
    html.Div([
        html.Div([
            html.H6('Total Cases', style={'color': '#0000FF'}),
        ], className="three columns"),
        html.Div([
            html.H6('Deaths', style={'color': '#FF0000'}),
        ], className="three columns"),
        html.Div([
            html.H6('Recovered', style={'color': '#00FF00'}),
        ], className="three columns"),
        html.Div([
            html.H6('Active', style={'color': '#FFA500'}),
        ], className="three columns"),
    ], className="row"),
    html.Div([
        html.Div(children=[totalCases,
                           ], className="three columns"),
        html.Div(children=[totalDeaths,
                           ], className="three columns"),
        html.Div(children=[totalRecovered,
                           ], className="three columns"),
        html.Div(children=[activeCases,
                           ], className="three columns"),
    ], className="row"),
    html.Div([
        html.Div([
            html.Footer('Data source from https://www.worldometers.info/coronavirus/#countries  @Mar 2020',
                        style={'text-align': 'center', 'color': '#000000', 'font-size': 10, 'font-weight': 'bold'}),
        ])
    ])
])

# Run the function in another thread
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)

if __name__ == '__main__':
    app.run_server(debug=True)
