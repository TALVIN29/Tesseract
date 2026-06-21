# tests/test_crud_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_docs():
    r = client.get("/api/docs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_graph_shape():
    r = client.get("/api/graph")
    data = r.json()
    assert "nodes" in data and "edges" in data


def test_get_doc_missing():
    r = client.get("/api/docs/knowledge%2Fnonexistent%2Ffile.md")
    assert r.status_code == 404


def test_hub_endpoint():
    r = client.get("/api/hub/engineering/skill")
    assert r.status_code == 200
    assert "content" in r.json()
