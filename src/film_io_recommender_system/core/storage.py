from dotenv import load_dotenv
import os
import psycopg

load_dotenv(".env.local")

recommender_url = os.getenv("RECOMMENDER_CONNECTION_URL")
SAVE_QUERY = "INSERT INTO user_preferences (user_id, film_ids, updated_at) VALUES (%s, %s, now()) ON CONFLICT (user_id) DO UPDATE SET film_ids = EXCLUDED.film_ids, updated_at = now()"
READ_QUERY = "SELECT film_ids FROM user_preferences WHERE user_id = %s"

# WRITE
def save_preferences(user_id: str, film_ids: list[int]):

    with psycopg.connect(recommender_url) as conn:
        psycopg.connect(recommender_url, connect_timeout=10)

        with conn.cursor() as cur:
            cur.execute(SAVE_QUERY, (user_id, list(dict.fromkeys(film_ids))))   

#READ
def get_preferences(user_id: str):
    with psycopg.connect(recommender_url) as conn:

        with conn.cursor() as cur:
            cur.execute(READ_QUERY, (user_id,))

            row = cur.fetchone()
            if row is None: return []
            return row[0]


