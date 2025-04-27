import os
import requests
import time
import streamlit as st
from streamlit_lottie import st_lottie
import json

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
# 2. SESSION STATE
# -------------------------------
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = ""

# -------------------------------
# 3. GLOBAL STYLING
# -------------------------------
st.markdown("""<style> ... (your CSS here) ... </style>""", unsafe_allow_html=True)

# -------------------------------
# 4. HEADER
# -------------------------------
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 class="title-text">NOURISH AI</h1>
    <p class="subtitle-text">Professional Recipe Generator</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 5. LOAD LOTTIE FILES
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
# 6. SHOW LOTTIE
# -------------------------------
def show_lottie_animation(animation_data, speed=1, height=300, width=300, key_suffix=""):
    if animation_data:
        st.markdown("""<div style="background-color:#FFFFFF; padding:1rem; border-radius:12px; text-align:center;">""", unsafe_allow_html=True)
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
# 7. LAYOUT
# -------------------------------
col_input, col_anim, col_output = st.columns([1, 0.8, 1])

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

with col_anim:
    if st.session_state.generate_clicked and lottie_data:
        show_lottie_animation(lottie_data, key_suffix="1")
    if st.session_state.generate_clicked and lottie_data_2:
        show_lottie_animation(lottie_data_2, key_suffix="2")

with col_output:
    if st.session_state.generate_clicked:
        with st.spinner("Analyzing ingredients and generating recipes..."):
            time.sleep(1.2)
            try:
                response = requests.post(
                    "http://localhost:8000", 
                    json={"ingredients": st.session_state.ingredients}
                )

                if response.status_code == 200:
                    results = response.json()["recipes"]

                    st.markdown(f"""
                    <div style="margin-bottom: 1rem; text-align: center;">
                        <h2 style="font-size: 1.8rem; color: var(--text);">✨ RECOMMENDED RECIPES ✨</h2>
                        <p class="big-text">For: <strong>{st.session_state.ingredients}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    for recipe_info in results:
                        match = recipe_info["match_percentage"]
                        recipe = recipe_info["recipe_text"]
                        prep_time = np.random.randint(15, 60)
                        card_html = f"""
                        <div class="recipe-card">
                            <h3>{recipe}</h3>
                            <p class="big-text">🍳 <strong>{prep_time} minutes preparation</strong></p>
                            <p class="big-text">⭐ <strong>{match}% ingredient match</strong></p>
                            <div style="height: 20px; background: var(--primary);
                                        width: {match}%; border-radius: 8px; margin: 1rem 0;"></div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.error("Error fetching recipe suggestions.")

            except Exception as e:
                st.error(f"API error: {str(e)}", icon="❌")

# -------------------------------
# 8. SUPPRESS WARNINGS
# -------------------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
