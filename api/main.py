from fastapi import FastAPI
from pydantic import BaseModel
import openai

# Initialize FastAPI app
app = FastAPI()

# SET YOUR API KEY HERE (REPLACE THIS WITH YOUR ACTUAL KEY)
openai.api_key = "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"

# Define request body structure
class Query(BaseModel):
    ingredients: str

# Define the /suggest endpoint
@app.post("/suggest")
def suggest_recipe(query: Query):
    prompt = f"Given the following ingredients: {query.ingredients}, provide a detailed recipe including the title and step-by-step instructions."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides cooking recipes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        recipe = response['choices'][0]['message']['content'].strip()

        return {
            "ingredients": query.ingredients,
            "recipe": recipe
        }

    except openai.error.OpenAIError as e:
        return {"error": str(e)}
