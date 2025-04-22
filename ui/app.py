import requests
import streamlit as st

st.set_page_config(page_title="NourishAI", layout="centered")

st.title("👨‍🍳 NourishAI - Recipe Generator")
st.subheader("Enter your ingredients and get recipe matches!")

# Input
ingredients = st.text_area("Ingredients (comma separated):", placeholder="e.g. chicken, garlic, lemon")

if st.button("🔍 Generate Recipes"):
    if not ingredients.strip():
        st.warning("Please enter some ingredients.")
    else:
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    "http://localhost:8000/suggest",  # Local FastAPI endpoint
                    json={"ingredients": ingredients}
                )
                if response.status_code == 200:
                    output = response.json()["recipe"]
                    st.success("✅ Recipes generated:")
                    st.markdown(f"<pre style='background:#f9f9f9; padding:1rem'>{output}</pre>", unsafe_allow_html=True)
                else:
                    st.error("❌ API error. Check the backend.")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
