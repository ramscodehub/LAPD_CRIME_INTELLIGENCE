# ============================
# 📦 Imports
# ============================
import pandas as pd
import numpy as np
import re
import os
import time
import requests
import joblib
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import nltk

nltk.download('punkt', download_dir="./nltk_data")
nltk.download("punkt_tab", download_dir="./nltk_data")
nltk.data.path.append("./nltk_data")


# ============================
# 🕒 Timer Start
# ============================
start_time = time.time()

# ============================
# 📁 Load and Clean Dataset
# ============================
df = pd.read_csv("crimeProfileText_data.csv")  # Full profiles
df = df.sample(3000, random_state=42).reset_index(drop=True)

# ============================
# 🔤 Text Cleaning
# ============================
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return ' '.join(word_tokenize(text))

df['Clean_Profile'] = df['Crime_Profile_Text'].fillna('').apply(clean_text)

# ============================
# 🤖 Embedding Model
# ============================
model_st = SentenceTransformer("all-mpnet-base-v2")
#print("🔄 Generating embeddings...")
#text_embeddings = model_st.encode(df['Clean_Profile'].tolist(), show_progress_bar=True)
#np.save('text_embeddings.npy', text_embeddings)
text_embeddings = np.load('text_embeddings_for_severity_score.npy')


# ============================
# 🎯 Proxy Labeling
# ============================
def generate_proxy_score(text):
    score = 0
    if any(w in text for w in ['murder', 'homicide', 'gun', 'dead', 'shoot']):
        score += 8
    elif 'assault' in text or 'weapon' in text:
        score += 6
    elif 'robbery' in text or 'burglary' in text:
        score += 5
    elif 'fraud' in text or 'identity' in text:
        score += 3
    elif 'theft' in text:
        score += 2
    return min(score, 10)

df['Severity_Score'] = df['Clean_Profile'].apply(generate_proxy_score)

# ============================
# ✅ Train or Load Regressor
# ============================
model_path = "severity_regressor.pkl"
if os.path.exists(model_path):
    regressor = joblib.load(model_path)
    print("✅ Regressor loaded from disk.")
else:
    print("🎯 Training Random Forest Regressor...")
    X = text_embeddings
    y = df['Severity_Score'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    regressor.fit(X_train, y_train)
    joblib.dump(regressor, model_path)
    print("✅ Regressor trained and saved.")

# ============================
# 📘 Load MOCODE Map
# ============================
mocode_df = pd.read_csv("mocode_data.csv")
mocode_df['mocode_str'] = mocode_df['mocode'].astype(int).astype(str).str.zfill(4)
mocode_mapping = dict(zip(mocode_df['mocode_str'], mocode_df['description']))

def map_mocodes_to_text(mocode_input):
    codes = mocode_input.strip().split()
    return ", ".join([mocode_mapping.get(code.zfill(4), f"Unknown({code})") for code in codes])

# ============================
# 🤖 LLM Refinement
# ============================
groq_api_key = "API-KEY"

groq_url = "https://api.groq.com/openai/v1/chat/completions"

def refine_score_with_llm(crime_text, model_score):
    prompt = f"""
You are an expert in crime severity evaluation. Analyze the case:

\"\"\"{crime_text}\"\"\"

A model predicted severity score of {model_score}/10.

Assess if the score reflects the gravity of the case. If yes, return the same. If not, return your corrected severity score (just the number). 
Your response should be objective and severity-based.
Respond ONLY with the number. Then provide 3 case specific detailed preventive awareness tips for the victim based on this case.

Respond in JSON with:
{{
  "final_score": float between 0-10,
  "tips": ["tip 1", "tip 2", "tip 3"]
}}
"""
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }

    try:
        response = requests.post(groq_url, headers=headers, json=payload)
        parsed = response.json()['choices'][0]['message']['content']
        import json
        result = json.loads(parsed)
        return round(result.get("final_score", model_score), 2), result.get("tips", [])
    except Exception as e:
        print("LLM error:", e)
        return round(model_score, 2), []

# ============================
# 🧪 Inference on New Victim Input
# ============================
def generate_crime_profile(vict_age, vict_sex, vict_descent, crime_desc, premis, area, time_day, day, month, year, mocodes, weapon):
    sex_full = {"F": "Female", "M": "Male", "X": "Unknown"}.get(vict_sex.upper(), "Unknown")
    descent_full = {
        'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
        'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
        'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
        'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
        'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
    }.get(vict_descent.upper(), "Unknown")

    season = {12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',6:'Summer',7:'Summer',8:'Summer',9:'Fall',10:'Fall',11:'Fall'}.get(month, "Unknown")
    time_desc = { 'Morning': 'morning', 'Afternoon': 'afternoon', 'Evening': 'evening', 'Night': 'night' }.get(time_day, "unknown")
    month_name = ['January','February','March','April','May','June','July','August','September','October','November','December'][month-1]

    age_group = "child" if vict_age < 18 else "adult" if vict_age <= 60 else "senior"
    mocode_text = map_mocodes_to_text(mocodes)

    return " ".join([
        f"The victim was an {age_group} individual (age {vict_age}), identified as {sex_full} of {descent_full} descent.",
        f"They were involved in a reported case of {crime_desc.lower()}, which occurred at a {premis.lower()}.",
        f"The incident took place during the {time_desc} hours, in {month_name} ({season} season), on a {day} in the year {year}, within the {area} area.",
        f"The suspect's behavior included: {mocode_text.lower()}, and the weapon used was: {weapon.lower()}."
    ])

def predict_severity_from_inputs(**kwargs):
    profile_text = generate_crime_profile(**kwargs)
    cleaned = clean_text(profile_text)
    emb = model_st.encode([cleaned])
    model_score = regressor.predict(emb)[0]
    final_score, tips = refine_score_with_llm(profile_text, model_score)
    return final_score, tips, profile_text
