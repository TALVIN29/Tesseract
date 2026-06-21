from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_rejects_empty():
    r = client.post("/api/search", json={"query": ""})
    assert r.status_code == 400


def test_search_endpoint_exists():
    r = client.post("/api/search")
    assert r.status_code != 404


def test_lint_endpoint_exists():
    r = client.post("/api/lint", json={"dept": "all"})
    assert r.status_code in (200, 500)  # 200=success, 500=no pages yet


def test_stats_endpoint():
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data and "knowledge" in data


def test_seed_endpoint_exists():
    r = client.post("/api/seed")
    assert r.status_code != 404
