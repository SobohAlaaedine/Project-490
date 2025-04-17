import os
import json
import requests
import joblib
import numpy as np
import time
import streamlit as st
from streamlit_lottie import st_lottie

# -------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="NourishAI Pro | Chef System",
    page_icon="👨‍🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 2. LOAD MODEL (CACHED)
# -------------------------------
@st.cache_resource
def load_model():
    file_id = '1tR6_8S-yISRKZR2QJ6BjU3A3V5HHUCm7'
    destination = 'recipe_model.pkl'

    if not os.path.exists(destination):
        URL = f'https://drive.google.com/uc?id={file_id}'
        session = requests.Session()
        response = session.get(URL, stream=True)
        if 'Content-Disposition' in response.headers:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(32768):
                    f.write(chunk)

    model_data = joblib.load(destination)
    return {
        "model": model_data["model"],
        "vectorizer": model_data["vectorizer"],
        "label_encoder": model_data["label_encoder"]
    }

model_data = load_model()

# -------------------------------
# 3. SESSION STATE
# -------------------------------
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = ""

# -------------------------------
# 4. GLOBAL STYLING
# -------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
    --primary: #1E90FF;
    --bg: #FFFFFF;
    --card: #FFFFFF;
    --text: #1E90FF;
    --input: #FFFFFF;
    --border: #87CEFA;
}
body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Roboto', sans-serif;
}
.title-text {
    font-size: 6rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #2E3C49;
}
.subtitle-text {
    font-size: 2rem;
    font-weight: 500;
    margin-bottom: 2rem;
    color: #2E3C49;
}
div[data-testid="stTextArea"] label {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #2E3C49 !important;
}
.stTextArea textarea {
    font-size: 1.6rem;
    padding: 1.5rem;
    background: var(--input);
    border: 2px solid var(--border);
    border-radius: 12px;
    min-height: 200px;
    color: var(--text);
}
.stButton>button {
    font-size: 1.6rem;
    padding: 1rem 2rem;
    background: var(--primary);
    color: #FFF;
    border: none;
    border-radius: 12px;
    margin-top: 1.5rem;
    width: 100%;
}
.stButton>button:hover {
    background: #1A7AD9;
}
.recipe-card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 2px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: var(--text);
}
.recipe-card h3 {
    font-size: 1.6rem;
    margin-bottom: 1rem;
    color: var(--text);
}
.big-text {
    font-size: 1.4rem;
    line-height: 1.6;
    color: var(--text);
}
.photo-container {
    width: 100%;
    padding-top: 100%;
    position: relative;
    margin: 0 auto;
}
.photo-container img {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 5. HEADER
# -------------------------------
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 class="title-text">NOURISH AI</h1>
    <p class="subtitle-text">Professional Recipe Generator</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 6. LOAD LOTTIE FILES
# -------------------------------
def load_lottie_file(filename):
    path = os.path.join(r"C:\Users\AUB\Documents\GitHub\EECE-490", filename)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return None
    return None

lottie_data = load_lottie_file("Animation.json")
lottie_data_2 = load_lottie_file("Animation1.json")

# -------------------------------
# 7. SHOW LOTTIE ANIMATION
# -------------------------------
def show_lottie_animation(animation_data, speed=1, height=300, width=300, key_suffix=""):
    if animation_data:
        st.markdown(
            f"""<div style="background-color:#FFFFFF; padding:1rem; border-radius:12px; text-align:center;">""",
            unsafe_allow_html=True
        )
        st_lottie(
            animation_data,
            speed=speed,
            reverse=False,
            loop=True,
            quality="high",
            height=height,
            width=width,
            key=f"anim_{key_suffix}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# 8. LAYOUT
# -------------------------------
col_input, col_anim, col_output = st.columns([1, 0.8, 1])

# INPUT + IMAGES
with col_input:
    ingredients = st.text_area(
        "ENTER INGREDIENTS (COMMA SEPARATED):",
        height=200,
        placeholder="e.g., chicken breast, garlic, olive oil, fresh basil...",
        key="main_input"
    )
    if st.button("🔍 GENERATE RECIPES", key="main_button"):
        if not ingredients.strip():
            st.error("Please enter ingredients to continue", icon="⚠️")
            st.session_state.generate_clicked = False
        else:
            st.session_state.generate_clicked = True
            st.session_state.ingredients = ingredients

    st.markdown("<hr style='border: none; height: 2px; background: var(--border);'>", unsafe_allow_html=True)

    image_urls = [
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836"
    ]

    for i in range(0, 4, 2):
        row = st.columns(2)
        for j in range(2):
            with row[j]:
                st.markdown(f"""
                <div class="photo-container">
                    <img src="{image_urls[i + j]}" alt="Photo {i + j + 1}">
                </div>
                """, unsafe_allow_html=True)

# ANIMATIONS
with col_anim:
    if st.session_state.generate_clicked and lottie_data:
        show_lottie_animation(lottie_data, key_suffix="1")
    if st.session_state.generate_clicked and lottie_data_2:
        show_lottie_animation(lottie_data_2, key_suffix="2")

# OUTPUT RECIPES
with col_output:
    if st.session_state.generate_clicked:
        with st.spinner("Analyzing ingredients and generating recipes..."):
            time.sleep(1.2)
            try:
                X_input = model_data["vectorizer"].transform([st.session_state.ingredients]).toarray()
                y_pred = model_data["model"].predict(X_input)
                top3_indices = np.argsort(y_pred, axis=1)[0][-3:][::-1]
                top3_recipes = model_data["label_encoder"].inverse_transform(top3_indices)
                top3_scores = (y_pred[0][top3_indices] * 100).astype(int)

                st.markdown(f"""
                <div style="margin-bottom: 1rem; text-align: center;">
                    <h2 style="font-size: 1.8rem; color: var(--text);">✨ RECOMMENDED RECIPES ✨</h2>
                    <p class="big-text">For: <strong>{st.session_state.ingredients}</strong></p>
                </div>
                """, unsafe_allow_html=True)

                for recipe_name, score in zip(top3_recipes, top3_scores):
                    prep_time = np.random.randint(15, 60)
                    card_html = f"""
                    <div class="recipe-card">
                        <h3>{recipe_name}</h3>
                        <p class="big-text">🍳 <strong>{prep_time} minutes preparation</strong></p>
                        <p class="big-text">⭐ <strong>{score}% ingredient match</strong></p>
                        <div style="height: 20px; background: var(--primary);
                                    width: {score}%; border-radius: 8px; margin: 1rem 0;"></div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analysis error: {str(e)}", icon="❌")

# -------------------------------
# 9. SUPPRESS TENSORFLOW WARNINGS
# -------------------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
