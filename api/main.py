from fastapi import FastAPI
from pydantic import BaseModel
import faiss, pickle, numpy as np, os
from sentence_transformers import SentenceTransformer
from openai import AzureOpenAI

# Azure OpenAI Settings
endpoint = "https://aos08-m9r3fgwd-uaenorth.cognitiveservices.azure.com/"
deployment = "gpt-4o"  # Your Azure deployment name
api_version = "2024-12-01-preview"
subscription_key = os.getenv("AZURE_OPENAI_KEY")

# Init AzureOpenAI client
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# FastAPI init
app = FastAPI()

# Load model + FAISS index
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("models/recipes_index.faiss")

with open("models/titles.pkl", "rb") as f:
    titles = pickle.load(f)

# Query model
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

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are an expert chef."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    return {"recipe": response.choices[0].message.content.strip()}
