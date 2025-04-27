# ✅ Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')
# ✅ Install dependencies (only needed in Colab)
!pip install faiss-cpu sentence-transformers fastapi uvicorn nest-asyncio
# ✅ RAG FastAPI App Code
from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
import uvicorn

# Allow FastAPI to run inside Jupyter/Colab
nest_asyncio.apply()

# ✅ Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load from Google Drive
MODEL_PATH = "/content/drive/MyDrive/Final-Project-Files"

print("📦 Loading data...")
index = faiss.read_index(f"{MODEL_PATH}/recipes_index.faiss")
with open(f"{MODEL_PATH}/recipes_data.pkl", "rb") as f:
    rag_texts = pickle.load(f)
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model and index loaded.")

# ✅ Request schema
class Query(BaseModel):
    ingredients: str

# ✅ Endpoint for recipe suggestion
@app.post("/suggest")
def suggest_recipe(query: Query):
    # Encode user input
    q_embed = model.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q_embed)

    # Search top 3 similar recipes
    scores, ids = index.search(q_embed, k=3)

    # Format output
    results = []
    for i, idx in enumerate(ids[0]):
        recipe = rag_texts[idx]
        match = round(scores[0][i] * 100, 2)
        results.append(f"✅ Match: {match}%\n\n{recipe}")

    return {"recipe": "\n\n\n".join(results)}
