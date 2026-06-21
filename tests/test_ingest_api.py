from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_ingest_rejects_empty():
    r = client.post("/api/ingest", json={"text": ""})
    assert r.status_code == 400


def test_ingest_endpoint_exists():
    # Verify route registered (will fail with 422 if body missing, not 404)
    r = client.post("/api/ingest")
    assert r.status_code != 404
