from app.tmdb import format_movie

def rank_movies(movies, genre_id=0, min_rating=0, language="", min_year=0):
    recommendations = []

    for movie in movies:
        score = 0
        reasons = []

        if genre_id > 0 and genre_id in movie.get("genre_ids", []):
            score += 3
            reasons.append("Matches preferred genre")
        
        rating = movie.get("vote_average", 0)

        if min_rating > 0 and rating >= min_rating:
            score += 2
            reasons.append("Meets preferred rating")

        movie_language = movie.get("original_language", "")

        if language and movie_language == language:
            score += 1
            reasons.append("Matches preferred language")

        release_date = movie.get("release_date", "")

        if min_year > 0 and release_date:
            year_text = release_date[:4]

        release_year = int(year_text)

        if release_year >= min_year:
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

    return recommendations[:10]