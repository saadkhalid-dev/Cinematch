from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.recommender import rank_movies
from app.tmdb import (
    discover_movies,
    get_genres,
    get_movie_details,
    get_popular_movies,
    get_recommendation_candidates,
    search_movies
)

app = FastAPI(title = "CineMatch API")

# Specifies the preferences accepted by the recommendation endpoint.
class RecommendationRequest(BaseModel):
    genre_id: int = 0
    min_rating: float = 0
    language: str = ""
    min_year: int = 0

# Endpoint to verify if the API is up and running.
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/movies/search")
def search_movie_endpoint(query: str):
    movies = search_movies(query)

    return {
        "query": query,
        "results": movies
    }

@app.get("/movies/popular")
def popular_movies_endpoint():
    return {
        "results": get_popular_movies()
    }

@app.get("/genres")
def genres_endpoint():
    return {
        "genres": get_genres()
    }

@app.get("/movies/discover")
def discover_movies_endpoint(
    genre_id: int = 0,
    min_rating: float = 0,
    year: int = 0,
    language: str = ""
):

    # Validate the filters before forwarding to TMDB.
    if min_rating < 0 or min_rating > 10:
        raise HTTPException(
            status_code = 400,
            detail = "Minimum rating must be between 0 and 10"
        )

    if year < 0:
        raise HTTPException(
            status_code = 400,
            detail = "Year cannot be negative"
        )

    movies = discover_movies(genre_id, min_rating, year, language)

    return {
        "filters": {
            "genre_id": genre_id,
            "min_rating": min_rating,
            "year": year,
            "language": language
        },
        "results": movies
    }

@app.post("/recommendations")
def recommend_movies(preferences: RecommendationRequest):

    if preferences.min_rating < 0 or preferences.min_rating > 10:
        raise HTTPException(
            status_code = 400,
            detail = "Minimum rating must be between 0 and 10"
        )
    
    if preferences.min_year < 0:
        raise HTTPException(
            status_code = 400,
            detail = "Minimum year cannot be negative"
        )
    
    if (preferences.genre_id == 0
        and preferences.min_rating == 0
        and preferences.language == ""
        and preferences.min_year == 0):

        raise HTTPException(
            status_code = 400,
            detail = "At least one recommendation preference is required"
        )

    # Select appropriate movies from TMDB before using our rating system on them.
    candidates = get_recommendation_candidates(preferences.genre_id)

    # Rank the candidates in accordance with the user's preferences.
    recommendations = rank_movies(
        candidates,
        preferences.genre_id,
        preferences.min_rating,
        preferences.language,
        preferences.min_year
    )

    return {
        "preferences": {
            "genre_id": preferences.genre_id,
            "min_rating": preferences.min_rating,
            "language": preferences.language,
            "min_year": preferences.min_year
        },
        "result_count": len(recommendations),
        "recommendations": recommendations
    }

@app.get("/movies/{movie_id}")
def movie_details_endpoint(movie_id: int):
    return get_movie_details(movie_id)