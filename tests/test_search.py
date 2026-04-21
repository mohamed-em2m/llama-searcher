from llama_searcher.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_api_status():
    """
    Simulate a basic request to see if the engine handles 404s correctly
    and verify the FastAPI app is importable.
    """
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404


def test_search_endpoint_missing_params():
    """
    Verify the /search endpoint requires a query parameter.
    """
    response = client.get("/search")
    assert response.status_code == 422  # Unprocessable Entity
