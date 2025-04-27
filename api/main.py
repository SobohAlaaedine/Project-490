# ✅ FastAPI RAG App Code

from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio

# Allow FastAPI to run inside Jupyter/Colab
nest_asyncio.apply()

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAISS index and recipe data
MODEL_PATH = "/content/drive/MyDrive/Final-Project-Files"

print("📦 Loading FAISS index and recipes...")
index = faiss.read_index(f"{MODEL_PATH}/recipes_index.faiss")
with open(f"{MODEL_PATH}/recipes_data.pkl", "rb") as f:
    rag_texts = pickle.load(f)
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model and index loaded.")

# Request schema
class Query(BaseModel):
    ingredients: str

# Suggest endpoint
@app.post("/suggest")
def suggest_recipe(query: Query):
    if not query.ingredients.strip():
        return {"error": "No ingredients provided."}

    q_embed = model.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q_embed)

    scores, ids = index.search(q_embed, k=3)

    results = []
    for i, idx in enumerate(ids[0]):
        recipe = rag_texts[idx]
        match = round(scores[0][i] * 100, 2)
        results.append({
            "match_percentage": match,
            "recipe_text": recipe
        })

    return {"recipes": results}

# Optional: Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
