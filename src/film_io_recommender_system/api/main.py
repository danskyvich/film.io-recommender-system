from fastapi import Query, FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
import psycopg
from dotenv import load_dotenv
import secrets
import os
from film_io_recommender_system.core.storage import save_preferences, get_preferences
from film_io_recommender_system.core.recommender import generate_recommendations

app = FastAPI()

load_dotenv(".env.local")
recommender_api_key = os.getenv("RECOMMENDER_API_KEY")

if not recommender_api_key:
    raise(RuntimeError("RECOMMENDER_API_KEY is not set."))

def verify_key(x_api_key: str | None = Header(default=None)):
    if x_api_key is None:
        raise(HTTPException(status_code=401, detail="Invalid API key."))
    if not secrets.compare_digest(x_api_key.encode(), recommender_api_key.encode()):
        raise(HTTPException(status_code=401, detail="Invalid API key."))

class FilmsPayload(BaseModel):
    film_ids: list[int] = Field(min_length=1, max_length=5)

class RecommendedFilm(BaseModel):
    film_id: int
    score: float

class RecommendationWrapper(BaseModel):
    recommendations: list[RecommendedFilm]

@app.put("/v1/users/{user_id}/preferences", dependencies=[Depends(verify_key)])
def save_user_preferences(user_id: str, payload: FilmsPayload):
    try:
        save_preferences(user_id, payload.film_ids)
        return { "status": "preferences saved successfully" }
    except psycopg.OperationalError:
        raise(HTTPException(status_code=503, detail="Recommendation service unavailable"))

@app.get("/v1/users/{user_id}/recommendations", response_model=RecommendationWrapper, dependencies=[Depends(verify_key)])
def fetch_recommendations(user_id: str, limit: int =  Query(10, ge=1, le=30)):
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
