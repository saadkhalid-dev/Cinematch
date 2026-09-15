import os
import httpx

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

app = FastAPI(title = "CineMatch API")

class RecommendationRequest(BaseModel):
    genre_id: int = 0
    min_rating: float = 0
    language: str = ""
    min_year: int = 0

def format_movie(movie):
    return {
        "id": movie["id"],
        "title": movie.get("title", ""),
        "release_date": movie.get("release_date", ""),
        "rating": movie.get("vote_average", 0),
        "language": movie.get("original_language", ""),
        "overview": movie.get("overview", "")
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/movies/search")
def search_movies(query: str):
    url = "https://api.themoviedb.org/3/search/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    parameters = {
        "query": query
    }

    response = httpx.get(url, headers = headers, params = parameters)

    data = response.json()

    movies = []

    for movie in data["results"]:
        movies.append(format_movie(movie))

    return {
        "query": query,
        "results": movies
    }

@app.get("/movies/popular")
def get_popular_movies():
    url = "https://api.themoviedb.org/3/movie/popular"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    response = httpx.get(url, headers = headers)

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(
            status_code = response.status_code,
            detail = data.get("status_message", "TMDB request failed")
        )

    movies = []

    for movie in data["results"][:10]:
        movies.append(format_movie(movie))

    return {
        "results": movies
    }

@app.get("/genres")
def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = httpx.get(url, headers = headers)

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(
            status_code = response.status_code,
            detail = data.get("status_message", "TMDB request failed")
        )

    return {
        "genres": data["genres"]
    }

@app.get("/movies/discover")
def discover_movies(
    genre_id: int = 0,
    min_rating: float = 0,
    year: int = 0,
    language: str = ""
):
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

    url = "https://api.themoviedb.org/3/discover/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    parameters = {
        "sort_by": "popularity.desc"
    }

    if genre_id > 0:
        parameters["with_genres"] = genre_id

    if min_rating > 0:
        parameters["vote_average.gte"] = min_rating

    if year > 0:
        parameters["primary_release_year"] = year

    if language:
        parameters["with_original_language"] = language

    response = httpx.get(
        url,
        headers = headers,
        params = parameters
    )

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(
            status_code = response.status_code,
            detail = data.get("status_message", "TMDB request failed")
        )

    movies = []

    for movie in data["results"][:10]:
        movies.append(format_movie(movie))

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

    url = "https://api.themoviedb.org/3/discover/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    parameters = {
        "sort_by": "popularity.desc"
    }

    if preferences.genre_id > 0:
        parameters["with_genres"] = preferences.genre_id

    response = httpx.get(
        url,
        headers = headers,
        params = parameters
    )

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(
            status_code = response.status_code,
            detail = data.get("status_message", "TMDB request failed")
        )

    recommendations = []

    for movie in data["results"][:20]:
        score = 0
        reasons = []

        if (preferences.genre_id > 0 and preferences.genre_id in movie.get("genre_ids", [])):
            score += 3
            reasons.append("Matches preferred genre")
        
        rating = movie.get("vote_average", 0)

        if preferences.min_rating > 0 and rating >= preferences.min_rating:
            score += 2
            reasons.append("Meets preferred rating")
        
        language = movie.get("original_language", "")

        if preferences.language and language == preferences.language:
            score += 1
            reasons.append("Matches preferred language")
        
        release_date = movie.get("release_date", "")

        if preferences.min_year > 0 and release_date:
            release_year = int(release_date[:4])
        
            if release_year >= preferences.min_year:
                score += 1
                reasons.append("Released within preferred period")

        if score > 0:
            recommended_movie = format_movie(movie)
            recommended_movie["match_score"] = score
            recommended_movie["reasons"] = reasons
            recommendations.append(recommended_movie)
    
    recommendations.sort(key = lambda movie: (
                            movie["match_score"],
                            movie["rating"]
                        ), 
                        reverse = True
                    )
    
    top_recommendations = recommendations[:10]

    return {
        "preferences": {
            "genre_id": preferences.genre_id,
            "min_rating": preferences.min_rating,
            "language": preferences.language,
            "min_year": preferences.min_year
        },
        "result_count": len(top_recommendations),
        "recommendations": top_recommendations
    }

@app.get("/movies/{movie_id}")
def get_movie_details(movie_id: int):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = httpx.get(url, headers = headers)

    if response.status_code == 404:
        raise HTTPException(
            status_code = 404,
            detail = "Movie not found"
        )

    data = response.json()

    genres = []

    for genre in data.get("genres", []):
        genres.append(genre["name"])

    return {
        "id": data.get("id"),
        "title": data.get("title", ""),
        "release_date": data.get("release_date", ""),
        "rating": data.get("vote_average", 0),
        "language": data.get("original_language", ""),
        "runtime_minutes": data.get("runtime"),
        "genres": genres,
        "tagline": data.get("tagline", ""),
        "overview": data.get("overview", ""),
        "movie_status": data.get("status", "")
    }