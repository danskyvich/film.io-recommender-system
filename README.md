# Film.io's recommender engine
This repository contains the source code of the recommendation engine for [Film.io](https://github.com/danskyvich/film.io).

Film.io's recommendation engine is a microservice that utilizes a statistical method called **Text Frequency-Inverse Document Frequency (TF-IDF)** to determine the most similar and relatable items based on a set of input (in this case, the films the user picked during onboarding).

## How does it work?
It transforms each TMDB's movie's table row into a single string (separated by an underscore '_'). The following movie data is used to generate the string:

- `overview` - movie description
- `genres` - movie's genres. It is formatted into `genre_{genre_id}`
- `language` - the language of the film. It is formatted into an ISO 639-1 code: `lang_{en}`.
- `release_date` - full, release date of the film. It is formatted to only include the decade of its release (e.g 1990 -> 90, 2021 -> 21) into this: `decade_90`, `decade_21`

The result is stored in a separate column of the table which will act as the corpus, the source data, which lives in memory and inside a dataframe. TF-IDF then turns each string into numbers, with each token and word having its own column, which aggregates into a total of 2,167 columns. Using sklearn's built-in tfidf vectorizer, each film becomes a row of numbers based on how much it appears on the film's text (tf) times how rare it is across all films (idf).

**Similarity scores (sim)**

Similarity scores are then computed to compare the cosine similarity between the picked films and all films in the catalog. The representation of the user's taste is determined by the averaging of the pick's vectors. The result of these calculations is a 2d numpy array with `K x N shape`, in which a `K` row represents a picked/onboarding film, and a `N` columns represents a catalog film. `(5, 138)` totals to approximately 690 cells.

**Quality score (qual)**

The quality variable tells us how well-regard each film is. It is computed using the film's vote_count and vote_average variables, the catalog's average rating, and a vote threshold variable. Unlike the similarity scores, it does not depend on the user.

**Blend weights (simb & qualb)**

These are two variables that I chose to determine how both the similarity and quality affects the final score. Both of them totals to 1, and can be modified to adjust each's influence to the recommender.

The function is as follows:

`final_score_array = simb * sim + qualb * qual`

| Variable |	Description |
|:-------- |:------------ |
| simb |	A decimal that controls the influence of user-dependent similarity scores |
|qualb |	A decimal that controls the influence of user-independent quality scores |

**Final score**

The result is a score assigned to each film, composing the user's recommendations, inside an array. During the process of fetching recommendations, this array is then sorted and arranged to retrieve only its first 10 movies, controlled by the limit parameter in the recommender's API (defaults to 10)

## API Reference
**Save user preferences**

`PUT /v1/users/${user_id}/preferences`

| Parameter |	Type | Description |
|:------------ |:------------- |:-------- |
| user_id |	string |	**Required** Your Film.io account's user_id |
| film_ids |	int[] |	The user's picked films during onboarding |

**Fetch user recommendations**

`GET /v1/users/${user_id}/recommendations`

| Parameter |	Type |	Description |
|:--------- |:----- |:---------- |
| id |	string |	**Required** Your Film.io account's user_id |

## Installation
#### Prerequisites
- Python v3.12.6
- uv

#### Run locally

1. Run `git clone https://github.com/danskyvich/film.io-recommender-system` to clone this repository.
2. cd to the project (or open the project in VSCode if you have Github Desktop installed.
3. Set up your environmental variables. You will need two database projects to ensure loose coupling.
   `MAIN_DB_CONNECTION_URL`=`postgresql://<readonly_user>:<password>@<host>/<dbname>?sslmode=require`
   `RECOMMENDER_DB_URL`=`postgresql://<user>:<password>@<host>/<dbname>?sslmode=require`
5. Run `uv sync`.
6. Run `uv run uvicorn film_io_recommender_system.api.main:app --reload` from the project root.
7. Check `/health` to see if the server works.
8. Navigate to `/docs` to test the API.

## Tech stack
- Python (scikit-learn, pandas, scipy, FastAPI)
- Neon
- VSCode

## Authors
[@danskyvich](https://github.com/danskyvich)
