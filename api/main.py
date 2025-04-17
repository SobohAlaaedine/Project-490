from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import openai

app = FastAPI()

# Set API key directly
openai.api_key = "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"

# Load FAISS index and titles
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
        response = openai.chat.completions.create(
            model="gpt-4o",
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
