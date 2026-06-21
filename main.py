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


class IngestBody(BaseModel):
    text: str


class SearchBody(BaseModel):
    query: str


class LintBody(BaseModel):
    dept: str = "all"


def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


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
# SSE Ingest Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/ingest")
async def ingest(body: IngestBody):
    text = body.text.strip()
    if not text:
        raise HTTPException(400, "text required")

    async def generate():
        yield sse({"step": "classifying", "status": "running"})
        classification = await asyncio.to_thread(ai.classify, text)
        dept = classification.get("dept", "engineering")
        meeting_type = classification.get("type", "standup")
        yield sse({"step": "classifying", "status": "done",
                   "dept": dept, "type": meeting_type})

        yield sse({"step": "extracting", "status": "running"})
        items = await asyncio.to_thread(ai.extract, text)
        yield sse({"step": "extracting", "status": "done", "count": len(items)})

        from datetime import date as _date
        lines = [f"# {dept.title()} {meeting_type.title()} — {_date.today().isoformat()}\n"]
        actions = [i for i in items if i.get("category") == "ACTION"]
        decisions = [i for i in items if i.get("category") == "DECIDED"]
        deferred = [i for i in items if i.get("category") == "DEFERRED"]
        if actions:
            lines.append("## Actions")
            for a in actions:
                lines.append(f"- ACTION | {a.get('owner','?')} | {a.get('what','?')} | {a.get('deadline') or 'TBD'}")
        if decisions:
            lines.append("\n## Decisions")
            for d in decisions:
                lines.append(f"- DECIDED: {d.get('what','?')}")
        if deferred:
            lines.append("\n## Deferred")
            for d in deferred:
                lines.append(f"- DEFERRED: {d.get('what','?')} → {d.get('deadline') or 'TBD'}")
        record = "\n".join(lines)
        path = await asyncio.to_thread(store.save_meeting, dept, record)
        yield sse({"step": "saving", "status": "done", "path": path})

        yield sse({"step": "compiling", "status": "running"})
        wiki_pages = list_wiki_pages(dept)
        updates = await asyncio.to_thread(ai.compile_to_wiki, text, dept, wiki_pages)
        for page_name, new_content in updates.items():
            doc_id = f"knowledge/{dept}/{page_name}.md"
            if Path(doc_id).exists():
                old_content = Path(doc_id).read_text(encoding="utf-8")
                pid = queue_overwrite(doc_id, old_content, new_content)
                yield sse({"step": "compiling", "status": "pending",
                           "doc": doc_id, "pending_id": pid})
            else:
                await asyncio.to_thread(save_wiki_page, dept, page_name, new_content)
                upsert_doc(doc_id, new_content)
                yield sse({"step": "compiling", "status": "created", "doc": doc_id})

        upsert_doc(path, record)
        yield sse({"step": "indexed", "status": "done"})
        yield sse({"step": "complete", "pending_count": len(pending)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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


# ---------------------------------------------------------------------------
# SSE Search Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/search")
async def search(body: SearchBody):
    if not body.query.strip():
        raise HTTPException(400, "query required")

    async def generate():
        from store import chroma_search
        docs = await asyncio.to_thread(chroma_search, body.query, 5)
        if not docs:
            yield sse({"chunk": "No documents found. Ingest some content first."})
            return
        result = await asyncio.to_thread(ai.search, body.query, docs)
        for word in result.split(" "):
            yield sse({"chunk": word + " "})
            await asyncio.sleep(0.01)
        yield sse({"chunk": "", "done": True})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------------------------------------------------------------------
# SSE Lint Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/lint")
async def lint(body: LintBody):
    async def generate():
        if body.dept == "all":
            all_docs = list_all_docs()
            pages = {k: v for k, v in all_docs.items() if "knowledge" in k}
        else:
            pages = {f"knowledge/{body.dept}/{k}": v
                     for k, v in list_wiki_pages(body.dept).items()}
        if not pages:
            yield sse({"chunk": "No wiki pages found."})
            return
        result = await asyncio.to_thread(ai.lint_wiki, pages)
        for word in result.split(" "):
            yield sse({"chunk": word + " "})
            await asyncio.sleep(0.01)
        yield sse({"chunk": "", "done": True})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------------------------------------------------------------------
# SSE Seed Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/seed")
async def seed():
    async def generate():
        yield sse({"status": "cloning", "progress": 0})
        n = await asyncio.to_thread(
            seed_from_repo, "https://github.com/msitarzewski/agency-agents"
        )
        yield sse({"status": "done", "progress": n, "total": n})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------------------------------------------------------------------
# Stats Endpoint
# ---------------------------------------------------------------------------

@app.get("/api/stats")
def stats():
    from store import _col
    all_docs = list_all_docs()
    knowledge = sum(1 for p in all_docs if "knowledge" in p)
    meetings = sum(1 for p in all_docs if "meetings" in p)
    return {
        "total": _col.count(),
        "knowledge": knowledge,
        "meetings": meetings,
        "agency": _col.count() - len(all_docs),
    }
