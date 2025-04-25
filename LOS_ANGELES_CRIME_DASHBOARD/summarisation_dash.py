import os
import pandas as pd
import openai
from dash import Dash, dcc, html, Input, Output, State
from tqdm import tqdm
import time
from datetime import datetime
from dash.exceptions import PreventUpdate

# ------------------- Configuration -------------------

MODEL_ID = "llama3-70b-8192"
MODEL_ID = "llama-3.3-70b-versatile"
API_BASE = "https://api.groq.com/openai/v1"
CHUNK_SIZE = 50
DATA_PATH = "crimeProfileText_data.csv"

# ------------------- Model Interaction -------------------
def call_model(prompt, api_key):
    openai.api_key = api_key
    openai.api_base = API_BASE
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except (openai.error.RateLimitError, openai.error.APIConnectionError):
        time.sleep(10)
        return ""
    except Exception as e:
        return f"API Error: {e}"

def summarize_chunks(texts, instruction, api_key):
    summaries = []
    for i in tqdm(range(0, len(texts), CHUNK_SIZE), desc="Summarizing"):
        chunk = texts[i:i + CHUNK_SIZE]
        prompt = instruction + "\n\n" + "\n".join(chunk)
        summaries.append(call_model(prompt, api_key))
    return summaries

def merge_summaries(summaries, final_instruction, api_key):
    full_input = final_instruction + "\n\n" + "\n\n".join(summaries)
    return call_model(full_input, api_key)

# ------------------- Dash App -------------------

def create_layout_summariser():
    """Function to define the layout for the Dash app."""
    # Read the CSV and populate the dropdown options
    df = pd.read_csv(DATA_PATH)
    area_names = sorted(df['AREA NAME'].dropna().unique())
    dropdown_options = [{'label': name, 'value': name} for name in area_names]

    return html.Div([
        html.H1("LAPD Crime Report Summarizer", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif', 'color': '#007BFF'}),

        # Area name dropdown
        html.Div([
            html.Label("📍 Select Area Name:", style={'fontWeight': 'bold', 'fontSize': '1.1rem'}),
            dcc.Dropdown(
                id='area_name',
                placeholder='Select Area Name (e.g., Hollywood)',
                style={'width': '300px', 'margin': '10px auto', 'padding': '5px', 'borderRadius': '8px'},
                options=dropdown_options,  # directly populated options
                value='77th Street',  # Default value
                searchable=True,
                clearable=False,
            ),
        ], style={'textAlign': 'center'}),

        # Months back input
        html.Div([
            html.Label("📅 Months to Look Back:", style={'fontWeight': 'bold', 'fontSize': '1.1rem'}),
            dcc.Input(id='months_back', value = 1, type='number', placeholder='Enter months to look back (e.g., 6)', style={'margin': '10px', 'padding': '10px', 'borderRadius': '8px', 'border': '1px solid #007BFF'}),
        ], style={'textAlign': 'center'}),

        # Button to generate summary
        html.Div([
            html.Button('Generate Summary', id='generate-button', n_clicks=0, style={'margin': '10px', 'padding': '10px 20px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontWeight': 'bold'}),
        ], style={'textAlign': 'center'}),

        # Loading indicator and output display
        dcc.Loading(id="loading", type="circle", children=[
            html.Div(id="summary-output", style={'whiteSpace': 'pre-wrap', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f8f9fa', 'padding': '1rem', 'borderRadius': '0.5rem', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)', 'marginTop': '20px'})
        ]),

        # Error message
        html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px', 'fontSize': '1rem'})
    ])

def register_callbacks_summariser(app):
    """Function to register callbacks for the Dash app."""
    @app.callback(
        Output('summary-output', 'children'),
        Output('error-message', 'children'),
        Input('generate-button', 'n_clicks'),
        State('area_name', 'value'),
        State('months_back', 'value')
    )
    def generate_summary(n_clicks, area_name, months_back):
        if n_clicks < 1:
            raise PreventUpdate

        if not area_name or not months_back:
            return '', 'Please provide both Area Name and Months to Look Back.'

        try:
            print("Loading preprocessed data...")
            crime_data = pd.read_csv(DATA_PATH)
            crime_data['DATE OCC'] = pd.to_datetime(
                crime_data['DATE OCC'],
                format="%m/%d/%Y %I:%M:%S %p",
                errors='coerce'
            )

            cutoff_date = crime_data['DATE OCC'].max() - pd.DateOffset(months=months_back)
            filtered = crime_data[
                (crime_data['AREA NAME'] == area_name) &
                (crime_data['DATE OCC'] >= cutoff_date)
            ]

            texts = filtered['Crime_Profile_Text'].dropna().astype(str).tolist()
            if not texts:
                return '', f"No records found for {area_name} in the last {months_back} months."

            instruction = (
                f"You are a crime analyst summarizing LAPD reports for {area_name}. "
                "For each group of cases, provide a structured summary with:\n"
                "1. Top 3 crime types.\n"
                "2. Common locations.\n"
                "3. Victim demographics.\n"
                "4. Timing patterns.\n"
                "5. Notable trends or anomalies.\n"
                "6. Community safety tips."
            )

            api_key = "API_KEY"
            summaries = summarize_chunks(texts, instruction, api_key)

            final_instruction = (
                f"As a senior analyst, combine the following summaries into one structured report "
                f"for {area_name} for community safety review:"
            )

            final_summary = merge_summaries(summaries, final_instruction, api_key)

            return html.Div([
                html.H4(f"📋 **Summary for {area_name}**", style={'fontWeight': 'bold', 'color': '#007BFF'}),
                html.H5("**📌 Executive Summary:**", style={'fontWeight': 'bold', 'color': '#007BFF'}),
                html.Pre(final_summary, style={"whiteSpace": "pre-wrap", "backgroundColor": "#f8f9fa", "padding": "1rem", "borderRadius": "0.5rem", 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'})
            ]), ''
        except Exception as e:
            return '', f"Error: {str(e)}"


# ------------------- Running the App -------------------


# Running standalone
if __name__ == '__main__':
    app = Dash(__name__)
    app.layout = create_layout_summariser()
    register_callbacks_summariser(app)
    app.run(debug=True)
