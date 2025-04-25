import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
crime_data = pd.read_csv("./crime_data_cleaned_2020_present.csv")
crime_data['Month'] = crime_data['Month'].astype(str)

# Initialize app
app = dash.Dash(__name__)
app.title = "Crime Dashboard"

# Layout function
def app_layout(crime_data):
    return html.Div([
        html.H1("Compare Crime Statistics Between Two Areas"),
        
        html.Label("Select Two Areas to Compare:"),
        dcc.Dropdown(
            id='area-dropdown-compare',
            options=[{'label': area, 'value': area} for area in sorted(crime_data['AREA NAME'].unique())],
            value=[crime_data['AREA NAME'].unique()[0], crime_data['AREA NAME'].unique()[1]],
            multi=True
        ),
        
        html.Br(),
        dcc.Graph(id='crime-trend-comparison'),
        dcc.Graph(id='crime-type-comparison'),
        dcc.Graph(id='crime-severity-ratio-comparison'),
        dcc.Graph(id='descent-comparison'),
    ])

# Callback registration function
def register_callbacks_compare(app):
    @app.callback(
        Output('crime-trend-comparison', 'figure'),
        Output('crime-type-comparison', 'figure'),
        Output('crime-severity-ratio-comparison', 'figure'),
        Output('descent-comparison', 'figure'),
        Input('area-dropdown-compare', 'value')
    )
    def update_comparison_graphs(selected_areas):
        if not selected_areas or len(selected_areas) != 2:
            return go.Figure(), go.Figure(), go.Figure(), go.Figure()

        area_1_df = crime_data[crime_data['AREA NAME'] == selected_areas[0]]
        area_2_df = crime_data[crime_data['AREA NAME'] == selected_areas[1]]

        area_colors = {
            selected_areas[0]: "#1f77b4",  # soft blue
            selected_areas[1]: "#ff7f0e"   # soft orange
        }

        # Monthly crime trends
        trend_data = crime_data[crime_data['AREA NAME'].isin(selected_areas)]
        monthly_trends = trend_data.groupby(['AREA NAME', 'Month'])['DR_NO'].count().reset_index()
        monthly_trends_fig = px.line(
            monthly_trends,
            x='Month', y='DR_NO', color='AREA NAME',
            title='Monthly Crime Trends Comparison',
            labels={'DR_NO': 'Number of Crimes'},
            color_discrete_map=area_colors
        )

        # Top 10 Crime Types Comparison
        top_crimes_area_1 = area_1_df['Crm Cd Desc'].value_counts().head(10).reset_index()
        top_crimes_area_2 = area_2_df['Crm Cd Desc'].value_counts().head(10).reset_index()
        top_crimes_area_1.columns = ['Crime Type', 'Count']
        top_crimes_area_2.columns = ['Crime Type', 'Count']

        top_crimes_fig = px.bar(
            pd.concat([
                top_crimes_area_1.assign(Area=selected_areas[0]),
                top_crimes_area_2.assign(Area=selected_areas[1])
            ]),
            x='Crime Type', y='Count', color='Area', barmode='group',
            title='Top 10 Crime Types Comparison',
            color_discrete_map=area_colors
        )
        top_crimes_fig.update_layout(xaxis_tickangle=45, height = 700)


        # Crime Severity Ratio Comparison
        severity_count_area_1 = area_1_df['Crime Severity'].value_counts().reset_index()
        severity_count_area_2 = area_2_df['Crime Severity'].value_counts().reset_index()
        severity_count_area_1.columns = ['Severity', 'Count']
        severity_count_area_2.columns = ['Severity', 'Count']

        severity_ratio_fig = px.bar(
            pd.concat([
                severity_count_area_1.assign(Area=selected_areas[0]),
                severity_count_area_2.assign(Area=selected_areas[1])
            ]),
            x='Severity', y='Count', color='Area', barmode='group',
            title='Crime Severity Ratio Comparison',
            labels={'Count': 'Number of Crimes', 'Severity': 'Crime Severity'},
            color_discrete_map=area_colors
        )
        severity_ratio_fig.update_layout(height = 400)

        # Descent Comparison
        descent_map = {
            'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian', 'F': 'Filipino',
            'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican', 'I': 'American Indian/Alaskan Native',
            'J': 'Japanese', 'K': 'Korean', 'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander',
            'S': 'Samoan', 'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
        }

        descent_area_1 = area_1_df['Vict Descent'].map(descent_map).value_counts().reset_index()
        descent_area_2 = area_2_df['Vict Descent'].map(descent_map).value_counts().reset_index()
        descent_area_1.columns = ['Victim Descent', 'Count']
        descent_area_2.columns = ['Victim Descent', 'Count']

        descent_combined = pd.concat([
            descent_area_1.assign(Area=selected_areas[0]),
            descent_area_2.assign(Area=selected_areas[1])
        ])

        descent_fig = px.bar(
            descent_combined,
            x='Victim Descent', y='Count', color='Area', barmode='group',
            title='Victim Descent Comparison Between Areas',
            color_discrete_map=area_colors
        )

        return monthly_trends_fig, top_crimes_fig, severity_ratio_fig, descent_fig

# Set layout
app.layout = app_layout(crime_data)

# Register callbacks
register_callbacks_compare(app)

if __name__ == "__main__":
    app.run(debug=True)
