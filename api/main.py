from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os

app = FastAPI()

# -------------------------------
# Load FAISS index and titles
# -------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("models/recipes_index.faiss")

with open("models/titles.pkl", "rb") as f:
    titles = pickle.load(f)

# -------------------------------
# Load T5 model locally
# -------------------------------
tokenizer = AutoTokenizer.from_pretrained("t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

# -------------------------------
# Request body format
# -------------------------------
class Query(BaseModel):
    ingredients: str

# -------------------------------
# Generation function
# -------------------------------
def generate_instructions(ingredients: str, top_titles: list[str]) -> str:
    # Use the best title (top FAISS match)
    selected_title = top_titles[0]
    prompt = f"Ingredients: {ingredients}\nRecipe title: {selected_title}\nInstructions:"
    
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output_ids = model.generate(input_ids, max_length=200, num_beams=4, early_stopping=True)
    
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return generated_text.strip()

# -------------------------------
# Suggest endpoint
# -------------------------------
@app.post("/suggest")
def suggest_recipe(query: Query):
    # Step 1: Embed query and search
    q = embedder.encode([query.ingredients], convert_to_numpy=True)
    faiss.normalize_L2(q)
    scores, ids = index.search(q, k=3)

    # Step 2: Get top titles
    top_titles = [titles[i] for i in ids[0]]

    # Step 3: Generate step-by-step instructions
    instructions = generate_instructions(query.ingredients, top_titles)

    return {
        "ingredients": query.ingredients,
        "top_titles": top_titles,
        "instructions": instructions
    }
