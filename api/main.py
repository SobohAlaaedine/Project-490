from fastapi import FastAPI
from pydantic import BaseModel
import faiss, pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os

app = FastAPI()

# Load models and data
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("models/recipes_index.faiss")

with open("models/titles.pkl", "rb") as f:
    titles = pickle.load(f)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Query(BaseModel):
    ingredients: str

@app.post("/suggest")
def suggest_recipe(query: Query):
    q = embedder.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q)
    scores, ids = index.search(q, k=5)

    ctx_titles = "\n".join(f"- {titles[i]}" for i in ids[0])
    prompt = (
        f"I only have these ingredients: {query.ingredients}\n\n"
        f"The following recipe titles look relevant:\n{ctx_titles}\n\n"
        "Choose one and give me precise step-by-step instructions using ONLY the listed ingredients."
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert chef."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return {"recipe": completion.choices[0].message.content.strip()}
