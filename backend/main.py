from fastapi import FastAPI

app = FastAPI()


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Report that the backend is running."""
    return {"status": "ok"}
