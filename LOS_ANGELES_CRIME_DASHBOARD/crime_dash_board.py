import dash
from dash import dcc, html
import os

from area_crime_analysis import app1_layout, register_callbacks as register_callbacks_app1
from comparitive_crime_analysis import app_layout, register_callbacks_compare as register_callbacks_app2
from hotspot_detection import get_layout, register_callbacks_hotspots as register_callbacks_hotspots
from severity_score_2 import score_app_layout2, register_callbacks_severity
from NLPC5 import predict_severity_from_inputs
from summarisation_dash import create_layout_summariser, register_callbacks_summariser
import pandas as pd
import dash_bootstrap_components as dbc



crime_data = pd.read_csv("./crime_data_cleaned_2020_present.csv")
crime_data['Month'] = crime_data['Month'].astype(str)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE], suppress_callback_exceptions=True)

register_callbacks_app1(app)
register_callbacks_app2(app)
register_callbacks_hotspots(app)
register_callbacks_severity(app, predict_severity_from_inputs)
register_callbacks_summariser(app)



app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(
                src="./assets/police-badge.png",
                style={
                    'height': '40px',
                    'marginRight': '15px'
                }
            ),
            html.Div([
                html.H2("Los Angeles Crime Intelligence Dashboard", style={
                    'fontSize': '22px',
                    'margin': '0',
                    'color': '#ffffff',
                    'fontWeight': 'bold'
                }),
                html.P("Explore trends, compare areas, predict crime severity, and locate hotspots.", style={
                    'fontSize': '13px',
                    'margin': '0',
                    'color': '#dcdcdc'
                })
            ])
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'gap': '15px'
        })
    ], style={
        'textAlign': 'center',
        'padding': '10px',
        'backgroundColor': '#1e3d59',  # dark steel blue
        'borderBottom': '3px solid #58a4b0',  # teal/ice blue
        'boxShadow': '0 2px 6px rgba(0,0,0,0.15)'
    }),

    dcc.Tabs([
        dcc.Tab(label='Area Crime Analysis', children=[app1_layout()]),
        dcc.Tab(label='Comparitive Crime Analysis', children=[app_layout(crime_data)]),
        dcc.Tab(label='GEO HOTSPOTS', children=[get_layout()]),
        dcc.Tab(label='Crime Severity Analyzer', children=[score_app_layout2()]),
        dcc.Tab(label='Crime Summarizer', children=[create_layout_summariser()])
    ])
])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=False)
