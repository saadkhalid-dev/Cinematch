from fastapi import FastAPI

app = FastAPI(title = "CineMatch API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
