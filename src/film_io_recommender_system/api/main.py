from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import psycopg
from film_io_recommender_system.core.storage import save_preferences, get_preferences
from film_io_recommender_system.core.recommender import generate_recommendations

app = FastAPI()

class FilmsPayload(BaseModel):
    film_ids: list[int] = Field(min_length=1, max_length=5)

class RecommendedFilm(BaseModel):
    film_id: int
    score: float

class RecommendationWrapper(BaseModel):
    recommendations: list[RecommendedFilm]

@app.put("/v1/users/{user_id}/preferences")
def save_user_preferences(user_id: str, payload: FilmsPayload):
    save_preferences(user_id, payload.film_ids)
    return { "status": "preferences saved successfully" }

@app.get("/v1/users/{user_id}/recommendations", response_model=RecommendationWrapper)
def fetch_recommendations(user_id: str, limit: int = 10):
    try:
        user_preferences = get_preferences(user_id)
        recommendations = generate_recommendations(user_preferences, limit)
        transformed_recommendations = [{"film_id": film_id, "score": score} for film_id, score in recommendations]
        return { "recommendations": transformed_recommendations }
    except psycopg.OperationalError:
        raise(HTTPException(status_code=503, detail="Recommendation service unavailable"))

@app.get("/health")
def check_health():
    return { "message": "Ok" }
