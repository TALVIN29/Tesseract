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
