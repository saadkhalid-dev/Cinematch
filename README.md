# CineMatch API

CineMatch is a Python and FastAPI backend for movie discovery and explainable recommendations using real movie data from the TMDB API.

Users can search for movies, view popular titles, filter movies by preferences, retrieve detailed movie information and receive ranked recommendations with clear reasons for each match.

## Features

- Search movies by title
- View popular movies
- View detailed information for individual movies
- Browse available movie genres
- Discover movies by genre, rating, year and language
- Generate explainable movie recommendations
- Handle invalid requests and TMDB connection errors
- Automated testing with pytest

## Tech Stack

- Python
- FastAPI
- Pydantic
- HTTPX
- pytest
- TMDB REST API
- Git / GitHub

## Project Structure

```text
cinematch-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── tmdb.py
│   └── recommender.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_recommender.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

- `main.py` defines the FastAPI application, endpoints and request validation.
- `tmdb.py` handles communication with TMDB, authentication, formatting and external API errors.
- `recommender.py` contains the recommendation scoring and ranking logic.
- `tests/` contains automated API and recommendation tests.

## Recommendation System

CineMatch uses a simple rule-based scoring system:

| Preference | Points |
| --- | ---: |
| Preferred genre | +3 |
| Meets minimum rating | +2 |
| Preferred language | +1 |
| Released within preferred period | +1 |

Movies are ranked by match score, with TMDB rating used to break ties.

Each result also explains why it received its score.

Example:

```json
{
  "title": "Example Movie",
  "match_score": 7,
  "reasons": [
    "Matches preferred genre",
    "Meets preferred rating",
    "Matches preferred language",
    "Released within preferred period"
  ]
}
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Check that the API is running |
| GET | `/movies/search` | Search movies by title |
| GET | `/movies/popular` | View popular movies |
| GET | `/genres` | View available genres |
| GET | `/movies/discover` | Filter and discover movies |
| POST | `/recommendations` | Generate ranked recommendations |
| GET | `/movies/{movie_id}` | View detailed movie information |

FastAPI also provides interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/saadkhalid-dev/Cinematch.git
cd Cinematch
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Add your TMDB token

Create a `.env` file in the project root:

```text
TMDB_TOKEN=your_tmdb_read_access_token_here
```

The `.env` file is ignored by Git and should not be committed.

### 6. Run the API

```bash
python -m uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Example Recommendation Request

Send a `POST` request to:

```text
/recommendations
```

with:

```json
{
  "genre_id": 878,
  "min_rating": 7,
  "language": "en",
  "min_year": 2010
}
```

CineMatch retrieves suitable movie candidates from TMDB and ranks them using its own recommendation rules.

## Testing

Run all automated tests with:

```bash
python -m pytest -v
```

The tests cover API validation and recommendation behaviour while using mocked external data where appropriate.

## What I Learned

This project helped me practise:

- Python functions, lists, dictionaries, loops and conditionals
- Building REST APIs with FastAPI
- Query parameters, path parameters and JSON request bodies
- Consuming an external REST API
- Environment variables and API token handling
- HTTP status codes and error handling
- Refactoring code into separate modules
- Rule-based recommendation logic
- Automated testing with pytest and mocks
- Git and GitHub workflows

## Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

Movie data is provided by TMDB.