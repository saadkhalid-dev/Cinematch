import os
import httpx
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

TMBD_TOKEN = os.getenv("TMBD_TOKEN")

app = FastAPI(title = "CineMatch API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/movies/search")
def search_movies(query: str):
    url = "https://api.themoviedb.org/3/search/movie"

    headers = {
        "Authorization": f"Bearer {TMBD_TOKEN}"
    }

    parameters = {
        "query": query
    }

    response = httpx.get(url, headers=headers, params=parameters)

    data = response.json()

    movies = []

    for movie in data["results"]:
        movies.append({
            "id": movie["id"],
            "title": movie["title"],
            "release_date": movie.get("release_date", ""),
            "rating": movie.get("vote_average", 0),
            "overview": movie.get("overview", ""),
            "language": movie.get("original_language", "")
        })

    return {
        "query": query,
        "results": movies
    }
