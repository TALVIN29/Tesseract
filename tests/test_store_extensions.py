import pytest
from store import delete_doc, get_doc_meta, list_docs_meta, get_graph_data

def test_get_doc_meta_missing():
    m = get_doc_meta("knowledge/engineering/skill.md")
    assert "title" in m
    assert "updated_at" in m

def test_list_docs_meta_returns_list():
    result = list_docs_meta()
    assert isinstance(result, list)

def test_get_graph_data_shape():
    data = get_graph_data()
    assert "nodes" in data
    assert "edges" in data
    assert all("id" in n and "label" in n and "group" in n for n in data["nodes"])

def test_delete_doc_removes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "knowledge" / "engineering").mkdir(parents=True)
    p = tmp_path / "knowledge" / "engineering" / "test.md"
    p.write_text("hello")
    delete_doc("knowledge/engineering/test.md")
    assert not p.exists()
