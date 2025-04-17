from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize FastAPI app
app = FastAPI()

# Use your actual API key directly (since you requested it hardcoded)
client = OpenAI(api_key="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")

class Query(BaseModel):
    ingredients: str

@app.post("/suggest")
def suggest_recipe(query: Query):
    prompt = f"Given the following ingredients: {query.ingredients}, provide a detailed recipe including the title and step-by-step instructions."

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides detailed, professional cooking recipes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        recipe = completion.choices[0].message.content.strip()
        return {
            "ingredients": query.ingredients,
            "recipe": recipe
        }

    except Exception as e:
        return {"error": str(e)}
