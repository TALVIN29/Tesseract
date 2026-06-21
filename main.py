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
    index_all_docs, seed_from_repo,
)

app = FastAPI(title="Tesseract Knowledge Hub")
pending: dict[str, dict] = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    return Path("static/index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"ok": True}
