import os
import httpx
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

app = FastAPI(title = "CineMatch API")

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

    response = httpx.get(url, headers=headers, params=parameters)

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

    response = httpx.get(url, headers=headers)

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

@app.get("/movies/{movie_id}")
def get_movie_details(movie_id: int):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    response = httpx.get(url, headers=headers)

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