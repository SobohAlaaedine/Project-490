from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# ===========================
# Setup
# ===========================
app = FastAPI()

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# Load FAISS & Recipe Data
# ===========================
print("📦 Loading model and index...")
index = faiss.read_index("recipes_index.faiss")
with open("recipes_data.pkl", "rb") as f:
    rag_texts = pickle.load(f)
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Loaded")

# ===========================
# Request Model
# ===========================
class Query(BaseModel):
    ingredients: str

# ===========================
# Recipe Suggestion Endpoint
# ===========================
@app.post("/suggest")
def suggest_recipe(query: Query):
    q_embed = model.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q_embed)
    scores, ids = index.search(q_embed, k=3)

    results = []
    for i, idx in enumerate(ids[0]):
        recipe = rag_texts[idx]
        match = round(scores[0][i] * 100, 2)
        results.append(f"Match: {match}%\n\n{recipe}")

    return {"recipe": "\n\n\n".join(results)}
