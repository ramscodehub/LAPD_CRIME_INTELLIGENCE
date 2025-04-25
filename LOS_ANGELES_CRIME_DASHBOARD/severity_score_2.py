import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from NLPC5 import predict_severity_from_inputs

# Load area names from dataset
df = pd.read_csv("crimeProfileText_data.csv")
area_names = sorted(df["AREA NAME"].dropna().unique())

descent_full = {
    'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
    'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
    'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
    'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
    'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
}

# -------------------------
# 🧾 Layout
# -------------------------
def score_app_layout2():
    return dbc.Container([
        html.H2("🔍 Crime Severity Analyzer", className="text-center my-4"),

        # Store for crime history
        dcc.Store(id='crime_history_store', data=[]),

        dbc.Row([
            # Left Column - Input Fields
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Label("👤 Victim Age", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='vict_age', type='number', value=32, className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🚻 Victim Sex", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Dropdown(['M', 'F', 'X'], 'M', id='vict_sex', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🧬 Victim Descent", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Dropdown(
                        id='vict_descent',
                        options=[{'label': descent_full[key], 'value': key} for key in descent_full],
                        value='W',
                        className='form-control'
                    ), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("📄 Crime Description", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='crime_desc', value='Burglary', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🏠 Premise", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='premis', value='Residence', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("📍 Area", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Dropdown(
                        id='area',
                        options=[{'label': area, 'value': area} for area in area_names],
                        value=area_names[0],
                        className='form-control'
                    ), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🕒 Time of Day", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Dropdown(['Morning', 'Afternoon', 'Evening', 'Night'], 'Night', id='time_day', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("📅 Day of Week", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Dropdown(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'Sunday', id='day', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("📆 Month", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='month', type='number', value=3, min=1, max=12, className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("📅 Year", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='year', type='number', value=2024, className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🧾 MOCODES", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='mocodes', value='1300 0344', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Row([
                    dbc.Col(dbc.Label("🔫 Weapon Used", style={'fontWeight': 'bold'}), width=4),
                    dbc.Col(dcc.Input(id='weapon', value='Knife', className='form-control'), width=8)
                ], className='mb-3'),

                dbc.Button("Analyze", id='analyze_btn', color='primary', className='w-100'),
            ], width=6),

            # Right Column - Output
            dbc.Col([
                html.H5("🆕 Latest Crime Analysis", className='mt-3'),
                html.Div(id='latest_crime_output', style={'whiteSpace': 'pre-line', 'marginBottom': '20px'}),
                #html.Div(id='latest_crime_output', style={'whiteSpace': 'pre-line', 'marginBottom': '20px'}, dangerously_allow_html=True),


                html.H5("📊 Crime History (Sorted by Severity)", className='mt-4'),
                html.Div(id='crime_history_output', style={'whiteSpace': 'pre-line'}),
            ], width=6)
        ])
    ], fluid=True)


# -------------------------
# 🧠 Callbacks
# -------------------------
def register_callbacks_severity(app, predict_severity_from_inputs):
    @app.callback(
        Output('crime_history_store', 'data'),
        Output('latest_crime_output', 'children'),
        Input('analyze_btn', 'n_clicks'),
        State('vict_age', 'value'),
        State('vict_sex', 'value'),
        State('vict_descent', 'value'),
        State('crime_desc', 'value'),
        State('premis', 'value'),
        State('area', 'value'),
        State('time_day', 'value'),
        State('day', 'value'),
        State('month', 'value'),
        State('year', 'value'),
        State('mocodes', 'value'),
        State('weapon', 'value'),
        State('crime_history_store', 'data'),
        prevent_initial_call=True
    )
    def update_and_display(n_clicks, vict_age, vict_sex, vict_descent, crime_desc, premis, area,
                           time_day, day, month, year, mocodes, weapon, history):

        inputs = {
            "vict_age": vict_age, "vict_sex": vict_sex, "vict_descent": vict_descent,
            "crime_desc": crime_desc, "premis": premis, "area": area, "time_day": time_day,
            "day": day, "month": month, "year": year, "mocodes": mocodes, "weapon": weapon
        }

        score, tips, profile = predict_severity_from_inputs(**inputs)

        # Add new entry to history
        new_entry = {
            "score": score,
            "crime_desc": crime_desc, 
            "crime_profile" : profile
        }

        history.append(new_entry)

        # Latest output (full)
        tips_formatted = "\n".join(f"   - {tip}" for tip in tips)
        latest_output = f"🔥 Severity Score: {score}/10\n📝 Crime Profile:\n{profile}\n📢 Awareness Tips:\n{tips_formatted}"

        return history, latest_output

    @app.callback(
        Output('crime_history_output', 'children'),
        Input('crime_history_store', 'data')
    )
    def display_sorted_history(history):
        if not history:
            return "No previous crime history yet."

        # Exclude the latest crime (last one added)
        #sorted_history = sorted(history[:-1], key=lambda x: x['score'], reverse=True)
        sorted_history = sorted(history, key=lambda x: x['score'], reverse=True)


        result = []
        for idx, item in enumerate(sorted_history, 1):
            #block = f"{idx}. {item['crime_desc']} — Score: {item['score']}/10"
            block = (
            f"{idx}. {item['crime_desc']} — Score: {item['score']}/10\n"
            f"    📄 Profile: {item.get('crime_profile', 'N/A')}"
        )
            result.append(block)

        return "\n".join(result)


# -------------------------
# ▶️ Run App
# -------------------------
if __name__ == '__main__':
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
    app.title = "Crime Severity Analyzer"
    app.layout = score_app_layout2()
    register_callbacks_severity(app, predict_severity_from_inputs)
    app.run(debug=False)
