from app.recommender import rank_movies

def test_rank_movies_scores_best_match_first():
    movies = [
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
            "release_date": "2005-01-01",
            "vote_average": 9.0,
            "original_language": "fr",
            "overview": "Another test movie",
            "genre_ids": [18]
        }
    ]

    results = rank_movies(
        movies,
        genre_id = 878,
        min_rating = 7,
        language = "en",
        min_year = 2010
    )

    assert results[0]["title"] == "Perfect Match"
    assert results[0]["match_score"] == 7
    assert "Matches preferred genre" in results[0]["reasons"]
    assert "Meets preferred rating" in results[0]["reasons"]
    assert "Matches preferred language" in results[0]["reasons"]
    assert "Released within preferred period" in results[0]["reasons"]

def test_rank_movies_returns_maximum_ten():
    movies = []

    for movie_id in range(15):
        movies.append({
            "id": movie_id,
            "title": f"Movie {movie_id}",
            "release_date": "2020-01-01",
            "vote_average": 8.0,
            "original_language": "en",
            "overview": "Test movie",
            "genre_ids": [878]
        })

    results = rank_movies(
        movies,
        genre_id = 878,
        min_rating = 7,
        language = "en",
        min_year = 2010
    )

    assert len(results) == 10