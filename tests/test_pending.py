# tests/test_pending.py
from fastapi.testclient import TestClient
from main import app, pending

client = TestClient(app)


def test_pending_empty_by_default():
    pending.clear()
    r = client.get("/api/pending")
    assert r.json() == []


def test_approve_missing():
    r = client.post("/api/pending/nonexistent/approve")
    assert r.status_code == 404


def test_reject_missing():
    r = client.delete("/api/pending/nonexistent")
    assert r.status_code == 404


def test_queue_and_reject():
    from main import queue_overwrite
    pid = queue_overwrite("knowledge/test.md", "old", "new")
    assert pid in pending
    client.delete(f"/api/pending/{pid}")
    assert pid not in pending
