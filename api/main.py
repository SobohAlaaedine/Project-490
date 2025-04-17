from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI  # ✅ NEW SDK STYLE

app = FastAPI()

# Load your environment key
client = OpenAI(api_key=os.getenv("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"))  # ✅ NEW CLIENT INIT

# Load SentenceTransformer and FAISS index
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("models/recipes_index.faiss")

with open("models/titles.pkl", "rb") as f:
    titles = pickle.load(f)

class Query(BaseModel):
    ingredients: str

@app.post("/suggest")
def suggest_recipe(query: Query):
    q = embedder.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q)
    scores, ids = index.search(q, k=5)

    top_titles = [titles[i] for i in ids[0]]
    ctx_titles = "\n".join(f"- {t}" for t in top_titles)

    prompt = (
        f"I only have these ingredients: {query.ingredients}\n\n"
        f"The following recipe titles look relevant:\n{ctx_titles}\n\n"
        f"Choose one and give me a recipe with clear step-by-step instructions using only the listed ingredients."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # ✅ Make sure this model is available to you
            messages=[
                {"role": "system", "content": "You are a professional chef."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )

        return {
            "ingredients": query.ingredients,
            "top_titles": top_titles,
            "instructions": response.choices[0].message.content.strip()
        }
    except Exception as e:
        return {"error": str(e)}
