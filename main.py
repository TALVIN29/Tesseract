import asyncio
import json
import os
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import ai
import store
from store import (
    list_wiki_pages, save_wiki_page, append_log, upsert_doc,
    index_all_docs, seed_from_repo, delete_doc, get_doc_meta,
    list_docs_meta, get_graph_data, list_all_docs, build_backlinks,
    read_knowledge,
)


class DocUpdate(BaseModel):
    content: str

app = FastAPI(title="Tesseract Knowledge Hub")
pending: dict[str, dict] = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    return Path("static/index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/docs")
def list_docs():
    return list_docs_meta()


@app.get("/api/docs/{doc_id:path}")
def get_doc(doc_id: str):
    path = Path(doc_id)
    if not path.exists():
        raise HTTPException(404, "Document not found")
    return {"id": doc_id, "content": path.read_text(encoding="utf-8"),
            "metadata": get_doc_meta(doc_id)}


@app.put("/api/docs/{doc_id:path}")
def update_doc(doc_id: str, body: DocUpdate):
    path = Path(doc_id)
    if not path.exists():
        raise HTTPException(404, "Document not found")
    path.write_text(body.content, encoding="utf-8")
    upsert_doc(doc_id, body.content)
    return {"ok": True}


@app.delete("/api/docs/{doc_id:path}")
def remove_doc(doc_id: str):
    if not Path(doc_id).exists():
        raise HTTPException(404, "Document not found")
    delete_doc(doc_id)
    return {"ok": True}


@app.get("/api/graph")
def graph():
    return get_graph_data()


@app.get("/api/hub/{dept}/{doc}")
def hub(dept: str, doc: str):
    content = read_knowledge(dept, doc)
    backlinks = build_backlinks()
    linked_from = backlinks.get(f"{dept}/{doc}", [])
    return {"content": content, "backlinks": linked_from}


# ---------------------------------------------------------------------------
# HITL Pending Queue
# ---------------------------------------------------------------------------

def queue_overwrite(doc_id: str, old_content: str, new_content: str) -> str:
    pid = str(uuid.uuid4())
    pending[pid] = {
        "id": pid,
        "doc_id": doc_id,
        "old_content": old_content,
        "new_content": new_content,
    }
    return pid


@app.get("/api/pending")
def list_pending():
    return list(pending.values())


@app.post("/api/pending/{pid}/approve")
def approve_pending(pid: str):
    item = pending.pop(pid, None)
    if not item:
        raise HTTPException(404, "Pending item not found")
    path = Path(item["doc_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(item["new_content"], encoding="utf-8")
    upsert_doc(item["doc_id"], item["new_content"])
    return {"ok": True}


@app.delete("/api/pending/{pid}")
def reject_pending(pid: str):
    if pid not in pending:
        raise HTTPException(404, "Pending item not found")
    pending.pop(pid)
    return {"ok": True}
