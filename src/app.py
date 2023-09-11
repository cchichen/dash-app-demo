# Import packages
from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import csv
import requests
import plotly
import plotly.express as px
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv

load_dotenv()

key = "ALPHAVANTAGE_API_KEY"
apiKey = os.getenv(key)
# print(apiKey)

ts = TimeSeries(apiKey, output_format='pandas')

CSV_URL = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={apiKey}'

with requests.Session() as s:
    download = s.get(CSV_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)

    symbols = []
    for row in my_list:
       symbols.append(row[0])
    #    print(row)
    print(symbols)

# # get time series for a specific symbol
# ts = TimeSeries(key=YOUR_API_KEY)
# # Get json object with the intraday data and another with  the call's metadata
# data, meta_data = ts.get_intraday('GOOGL')
# print(meta_data)
# # Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# App layout
app.layout = html.Div([
    
    # html.Div(id='dd-output-container', className="menu",
    #          children=[html.Div(className="menu-item",children=[dcc.Dropdown(symbols[1:], "UNP", id='stock-dropdown',clearable=False)])
    # ,
    # html.Div(className="menu-item2",children=[dcc.Dropdown(symbols[1:], "UNP", id='stock-dropdown1', clearable=False)]),]),

    dbc.Container([
    dbc.Row([dbc.Col(dcc.Dropdown(symbols[1:], "UNP", id='stock-dropdown',clearable=False)), dbc.Col(dcc.Dropdown(symbols[1:], "UNL", id='stock-dropdown1',clearable=False))])
    ]),
    

    dcc.Graph(id="linechart"),
    dcc.Graph(id="combined")
    # dash_table.DataTable(data=data, page_size=10)
])

@callback(
    Output('combined', 'figure'),
    Output('linechart', 'figure'),
    Input('stock-dropdown', 'value'),
    Input('stock-dropdown1', 'value')
)
def update_output(dropdown1, dropdown2):
    ttm_data, ttm_meta_data = ts.get_intraday(symbol=f'{dropdown1   }',interval='1min',outputsize='compact')

    df = ttm_data.copy()
    df=df.transpose()
    df.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
                     "4. close":"close","5. volume":"volume"},inplace=True)
    df=df.reset_index().rename(columns={'index': 'indicator'})
    df = pd.melt(df,id_vars=['indicator'],var_name='date',value_name='rate')
    print(df)
    df = df[df['indicator']!='volume']


    IBM_data, IBM_meta_data = ts.get_intraday(symbol=f'{dropdown2}',interval='1min',outputsize='compact')

    df1 = IBM_data.copy()
    #print(df1)
    df1=df1.transpose()
    df1.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
                     "4. close":"close","5. volume":"volume"},inplace=True)
    df1=df1.reset_index().rename(columns={'index': 'indicator'})
    df1 = pd.melt(df1,id_vars=['indicator'],var_name='date',value_name='rate')
    #print(f'{df1}datahere')
    df1 = df1[df1['indicator']!='volume']
    print(df1)
    # fig1 = px.line(
    #             data_frame=df1,
    #             x='date',
    #             y='rate',
    #             color='indicator',
    #             title="Stock: {}".format(ttm_meta_data['2. Symbol'])
    #             )

    line_chart = go.Figure()
    
    line_chart.add_trace(go.Scatter(x=df['date'], y=df['rate'], name=f'{dropdown1}'))

    line_chart.add_trace(go.Scatter(x=df1['date'], y=df1['rate'], name=f'{dropdown2}'))

    line_chart.update_layout(
                  title_text="Combined Graph For Two Stocks")




    fig = make_subplots(rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02)
    fig.add_trace(go.Scatter(x=df['date'], y=df['rate'], name=f'{dropdown1}'),
              row=1, col=1)

    fig.add_trace(go.Scatter(x=df1['date'], y=df1['rate'], name=f'{dropdown2}'),
              row=2, col=1)

    fig.update_layout(
                  title_text="Stacked Subplots with Shared X-Axes")


    # line_chart = px.line(
    #             data_frame=df,
    #             x='date',
    #             y='rate',
    #             color='indicator',
    #             title="Stock: {}".format(ttm_meta_data['2. Symbol'])
    #             )
    # line_chart.add_trace(go.Scatter(df2, x=[1,8], y=[1,8]))
    return line_chart,fig
    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
