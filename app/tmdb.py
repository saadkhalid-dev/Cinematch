import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN", "").strip()

if not TMDB_TOKEN:
    raise RuntimeError("TMDB_TOKEN is missing from the .env file")

TMDB_BASE_URL = "https://api.themoviedb.org/3"

TMDB_HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}

def tmdb_get(endpoint, parameters=None, not_found_message=None):
    url = f"{TMDB_BASE_URL}{endpoint}"

    try:
        response = httpx.get(
            url,
            headers = TMDB_HEADERS,
            params = parameters,
            timeout = 10.0
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code = 504,
            detail = "TMDB request timed out"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code = 504,
            detail = "Could not connect to TMDB"
        )
    
    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code = 502,
            detail = "TMDB returned an invalid response"
        )

    if response.status_code == 404 and not_found_message:
        raise HTTPException(
            status_code = 404,
            detail = not_found_message
        )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code = 502,
            detail = data.get("status_message", "TMDB request failed")
        )
    
    return data

def format_movie(movie):
    return {
        "id": movie["id"],
        "title": movie.get("title", ""),
        "release_date": movie.get("release_date", ""),
        "rating": movie.get("vote_average", 0),
        "language": movie.get("original_language", ""),
        "overview": movie.get("overview", "")
    }

def search_movies(query):
    data = tmdb_get("/search/movie", {"query": query})

    movies = []

    for movie in data.get("results", []):
        movies.append(format_movie(movie))
    
    return movies

def get_popular_movies():
    data = tmdb_get("/movie/popular")

    movies = []

    for movie in data.get("results", [])[:10]:
        movies.append(format_movie(movie))
    
    return movies

def get_genres():
    data = tmdb_get("/genre/movie/list")

    return data.get("genres", [])

def discover_movies(genre_id = 0, min_rating = 0, year = 0, language = ""):
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

    data = tmdb_get("/discover/movie", parameters)

    movies = []

    for movie in data.get("results", [])[:10]:
        movies.append(format_movie(movie))

    return movies

def get_recommendation_candidates(genre_id = 0):
    parameters = {
        "sort_by": "popularity.desc"
    }

    if genre_id > 0:
        parameters["with_genres"] = genre_id

    data = tmdb_get("/discover/movie", parameters)

    return data.get("results", [])[:20]

def get_movie_details(movie_id):
    data = tmdb_get(f"/movie/{movie_id}", not_found_message="Movie not found")

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