import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the data
crime_data = pd.read_csv("./crime_data_cleaned_2020_present.csv")

def app1_layout():
    return html.Div([
        html.H1("Crime Analysis by Area"),
        dcc.Dropdown(
            id='area-name-dropdown',
            options=[{'label': i, 'value': i} for i in crime_data['AREA NAME'].unique()],
            value='Central',
            style={'width': '50%'}
        ),
        dcc.Graph(id='area-crime-type-bar'),
        dcc.Graph(id='area-crime-time-series'),
        dcc.Graph(id='hourly-crime-area-bar'),
        dcc.Graph(id='victim-sex-pie'),
        dcc.Graph(id='victim-descent-pie'),
        dcc.Graph(id='victim-age-group-bar'),
    ])


def register_callbacks(app):
    @app.callback(
        [Output('area-crime-type-bar', 'figure'),
         Output('area-crime-time-series', 'figure'),
         Output('hourly-crime-area-bar', 'figure'),
         Output('victim-sex-pie', 'figure'),
         Output('victim-descent-pie', 'figure'),
         Output('victim-age-group-bar', 'figure')],
        [Input('area-name-dropdown', 'value')]
    )
    def update_area_graphs(area_name):
        filtered_area_df = crime_data[crime_data['AREA NAME'] == area_name]

        # Area Crime Type Bar Chart
        area_counts = filtered_area_df['Crm Cd Desc'].value_counts().head(15).reset_index()
        area_counts.columns = ['Crime Type', 'Count']
        area_crime_type_bar = px.bar(area_counts, x='Crime Type', y='Count', color='Crime Type',
                                     title=f"Crime Type Distribution in {area_name}")

        # Time Series Chart (Monthly)
        time_series = filtered_area_df.groupby(['Month']).size().reset_index(name='Count')
        area_crime_time_series = px.line(time_series, x='Month', y='Count',
                                         title=f"Crime Trends in {area_name} (Monthly)")

        # Hourly Crime Bar
        hourly_counts = filtered_area_df['Hour'].value_counts().reset_index()
        hourly_counts.columns = ['Hour', 'Count']
        hourly_crime_area_bar = px.bar(hourly_counts, x='Hour', y='Count', color='Hour',
                                       title=f"Crime Distribution by Hour in {area_name}")

        # Victim Sex Pie
        victim_sex_counts = filtered_area_df['Vict Sex'].value_counts().reset_index()
        victim_sex_counts.columns = ['Victim Sex', 'Count']
        victim_sex_pie = px.pie(victim_sex_counts, names='Victim Sex', values='Count',
                                title=f"Victim Sex Distribution in {area_name}")

        # Victim Descent Pie
        victim_descent_counts = filtered_area_df['Vict Descent'].value_counts().reset_index()
        victim_descent_counts.columns = ['Victim Descent', 'Count']
        descent_map = {
            'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
            'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
            'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
            'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
            'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
        }
        victim_descent_counts['Victim Descent'] = victim_descent_counts['Victim Descent'].map(descent_map).fillna('Unknown')
        victim_descent_pie = px.pie(victim_descent_counts, names='Victim Descent', values='Count',
                                    title=f"Victim Descent Distribution in {area_name}")

        # Age Group Bar Chart
        age_bins = [0, 18, 35, 50, 65, 100]
        age_labels = ['0-18', '19-35', '36-50', '51-65', '66+']
        filtered_area_df['Age Group'] = pd.cut(filtered_area_df['Vict Age'], bins=age_bins, labels=age_labels, right=False)
        age_group_counts = filtered_area_df['Age Group'].value_counts().reset_index()
        age_group_counts.columns = ['Age Group', 'Count']
        victim_age_group_bar = px.bar(age_group_counts, x='Age Group', y='Count',
                                      title=f"Victim Age Group Distribution in {area_name}",
                                      color='Age Group',
                                      color_discrete_sequence=px.colors.qualitative.Set1)

        return (area_crime_type_bar, area_crime_time_series, hourly_crime_area_bar,
                victim_sex_pie, victim_descent_pie, victim_age_group_bar)

# Run the app
if __name__ == '__main__':
    app = dash.Dash(__name__)
    app.layout = app1_layout()
    register_callbacks(app)
    app.run(debug=True)
