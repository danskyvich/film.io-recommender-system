from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Films(BaseModel):
    films_id: list[int] = Field(min_length=0, max_length=4)

film = Films()

@app.get("/v1/users/{user_id}/recommendations")
def fetch_recommendations(user_id: str, films: film):
    return { "message": "not implemented yet" }

@app.put("/v1/users/{user_id}/preferences")
def retrieve_user_preferences(user_id: str):
    return { "message": "not implemented yet" }