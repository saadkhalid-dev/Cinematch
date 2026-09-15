from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_search_endpoint_returns_movies():
    fake_movies = [
        {
            "id": 157336,
            "title": "Interstellar",
            "release_date": "2014-11-05",
            "rating": 8.5,
            "language": "en",
            "overview": "A test overview"
        }
    ]

    with patch("app.main.search_movies", return_value = fake_movies):
        response = client.get(
            "/movies/search",
            params = {"query": "Interstellar"}
        )

    data = response.json()

    assert response.status_code == 200
    assert data["query"] == "Interstellar"
    assert data["results"][0]["title"] == "Interstellar"

def test_discover_rejects_invalid_rating():
    response = client.get("/movies/discover", params={"min_rating": 20})

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Minimum rating must be between 0 and 10"
    )

def test_recommendations_require_preference():
    response = client.post(
        "/recommendations",
        json={
            "genre_id": 0,
            "min_rating": 0,
            "language": "",
            "min_year": 0
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "At least one recommendation preference is required"
    )

def test_recommendations_endpoint_returns_ranked_movies():
    fake_candidates = [
        {
            "id": 1,
            "title": "Perfect Match",
            "release_date": "2020-01-01",
            "vote_average": 8.5,
            "original_language": "en",
            "overview": "Test movie",
            "genre_ids": [878]
        },
        {
            "id": 2,
            "title": "Partial Match",
            "release_date": "2000-01-01",
            "vote_average": 6.0,
            "original_language": "fr",
            "overview": "Another movie",
            "genre_ids": [18]
        }
    ]

    with patch("app.main.get_recommendation_candidates", return_value=fake_candidates):
        response = client.post(
            "/recommendations",
            json={
                "genre_id": 878,
                "min_rating": 7,
                "language": "en",
                "min_year": 2010
            }
        )

    data = response.json()

    assert response.status_code == 200
    assert data["result_count"] >= 1
    assert data["recommendations"][0]["title"] == "Perfect Match"
    assert data["recommendations"][0]["match_score"] == 7

def test_movie_details_endpoint():
    fake_movie = {
        "id": 157336,
        "title": "Interstellar",
        "release_date": "2014-11-05",
        "rating": 8.5,
        "language": "en",
        "runtime_minutes": 169,
        "genres": [
            "Adventure",
            "Drama",
            "Science Fiction"
        ],
        "tagline": "Test tagline",
        "overview": "Test overview",
        "movie_status": "Released"
    }

    with patch("app.main.get_movie_details", return_value=fake_movie):
        response = client.get("/movies/157336")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 157336
    assert data["title"] == "Interstellar"
    assert data["runtime_minutes"] == 169