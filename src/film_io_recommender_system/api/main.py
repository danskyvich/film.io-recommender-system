from fastapi import FastAPI
from pydantic import BaseModel, Field
import psycopg
from src.film_io_recommender_system.core.storage import save_preferences, get_preferences
from src.film_io_recommender_system.core.recommender import generate_recommendations

app = FastAPI()

class FilmsPayload(BaseModel):
    film_ids: list[int] = Field(min_length=1, max_length=5)

@app.put("/v1/users/{user_id}/preferences")
def save_user_preferences(user_id: str, payload: FilmsPayload):
    save_preferences(user_id, payload.film_ids)
    return { "status": "preferences saved successfully" }

@app.get("/v1/users/{user_id}/recommendations")
def fetch_recommendations(user_id: str):
    try:
        user_preferences = get_preferences(user_id)
        recommendations = generate_recommendations(user_preferences, limit=10)
        return { "status": "data received", "recommendations": recommendations }
    except psycopg.OperationalError as err:
        return { "message": f"Error: {err}" }

@app.get("/health")
def check_health():
    return { "message": "Ok" }
