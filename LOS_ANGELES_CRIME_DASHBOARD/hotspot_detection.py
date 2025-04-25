import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

import dash
from dash import dcc, html
import os

# Load data
crime_data = pd.read_csv(
    "./crime_data_cleaned_2020_present.csv",
    parse_dates=["DATE OCC"]
)

# Clean LAT/LON columns
crime_data['LAT'] = pd.to_numeric(crime_data['LAT'], errors='coerce')
crime_data['LON'] = pd.to_numeric(crime_data['LON'], errors='coerce')
crime_data.dropna(subset=['LAT', 'LON'], inplace=True)

# Default crime type
default_crime_type = "ATTEMPTED ROBBERY"

def get_layout():
    return html.Div([
        html.H2("LA Crime Hotspot Heatmap", style={'textAlign': 'center', 'color': '#2c3e50'}),

        html.Div([
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=crime_data["DATE OCC"].min(),
                max_date_allowed=crime_data["DATE OCC"].max(),
                start_date=crime_data["DATE OCC"].min(),
                end_date=crime_data["DATE OCC"].max(),
                display_format='YYYY-MM-DD'
            ),
            dcc.Dropdown(
                id='crime-type-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(crime_data["Crm Cd Desc"].unique())],
                value=[default_crime_type],
                placeholder="Select Crime Type",
                multi=True
            ),
            dcc.Dropdown(
                id='premis-dropdown',
                options=[{'label': p, 'value': p} for p in sorted(crime_data["Premis Desc"].unique())],
                placeholder="Select Crime Location Type",
                multi=True
            ),
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '10px',
            'width': '60%',
            'margin': 'auto',
            'paddingBottom': '20px'
        }),

        html.Div([
            dcc.Graph(id='crime-heatmap', config={'scrollZoom': True, 'displayModeBar': False}),
            html.H3("Top 10 Areas with the Most Crimes for Selected Filters", style={'textAlign': 'center', 'color': '#2c3e50'}),
            dcc.Graph(id='top-crime-locations', config={'displayModeBar': False})
        ], style={'width': '100%', 'padding': '20px'})
    ])

def register_callbacks_hotspots(app):
    @app.callback(
        [Output('crime-heatmap', 'figure'),
         Output('top-crime-locations', 'figure')],
        [Input('date-picker', 'start_date'),
         Input('date-picker', 'end_date'),
         Input('crime-type-dropdown', 'value'),
         Input('premis-dropdown', 'value')]
    )
    def update_charts(start_date, end_date, selected_crimes, selected_premises):
        filtered_df = crime_data[
            (crime_data["DATE OCC"] >= start_date) &
            (crime_data["DATE OCC"] <= end_date)
        ]

        if selected_crimes:
            filtered_df = filtered_df[filtered_df["Crm Cd Desc"].isin(selected_crimes)]
        else:
            filtered_df = filtered_df[filtered_df["Crm Cd Desc"] == default_crime_type]

        if selected_premises:
            filtered_df = filtered_df[filtered_df["Premis Desc"].isin(selected_premises)]

        # Heatmap
        heatmap_fig = px.density_mapbox(
            filtered_df,
            lat="LAT",
            lon="LON",
            radius=10,
            center=dict(lat=34.0522, lon=-118.2437),
            zoom=9.5,
            hover_data={
                'Crm Cd Desc': True,
                'Premis Desc': True,
                'DATE OCC': True,
                'LAT': False,
                'LON': False
            },
            mapbox_style="carto-darkmatter",
            color_continuous_scale="YlOrRd",
            title="Crime Density Heatmap"
        )
        heatmap_fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            font=dict(family="Arial", size=13, color="#ffffff")
        )

        # Bar chart
        top_n_df = filtered_df.groupby('AREA NAME').size().reset_index(name='Crime Count')
        top_n_df = top_n_df.sort_values(by='Crime Count', ascending=False).head(10)

        bar_chart_fig = px.bar(
            top_n_df,
            x='AREA NAME',
            y='Crime Count',
            title="Top 10 Areas with the Most Crimes for Selected Filters",
            labels={'AREA NAME': 'Area Name', 'Crime Count': 'Number of Crimes'},
            color='Crime Count',
            color_continuous_scale='Blues',
            template='plotly_dark'
        )
        bar_chart_fig.update_layout(
            xaxis={'title': 'Area Name'},
            yaxis={'title': 'Number of Crimes'},
            margin={"r": 0, "t": 50, "l": 0, "b": 40},
            font=dict(family="Arial", size=13, color="#ffffff")
        )

        return heatmap_fig, bar_chart_fig

if __name__ == "__main__":
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = get_layout()
    register_callbacks_hotspots(app)
    app.run()
