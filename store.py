import base64
import os
import re
import tempfile
from datetime import date
from pathlib import Path

import chromadb
from pyvis.network import Network

KNOWLEDGE_DIR = "knowledge"
MEETINGS_DIR = "meetings"

_chroma = chromadb.PersistentClient(path="./chroma_db")
_col = _chroma.get_or_create_collection("tesseract")


def read_knowledge(dept: str, doc_type: str) -> str:
    path = os.path.join(KNOWLEDGE_DIR, dept, f"{doc_type}.md")
    if not os.path.exists(path):
        return f"No {doc_type}.md found for department '{dept}'."
    with open(path, encoding="utf-8") as f:
        return f.read()


def append_knowledge(dept: str, doc_type: str, content: str) -> None:
    path = os.path.join(KNOWLEDGE_DIR, dept, f"{doc_type}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n\n{content}")


def save_meeting(dept: str, content: str) -> str:
    today = date.today().isoformat()
    filename = f"{today}-{dept}.md"
    path = os.path.join(MEETINGS_DIR, filename)
    os.makedirs(MEETINGS_DIR, exist_ok=True)
    if os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n{content}")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return path


def list_all_docs() -> dict:
    docs = {}
    for base in (KNOWLEDGE_DIR, MEETINGS_DIR):
        if not os.path.exists(base):
            continue
        for root, _, files in os.walk(base):
            for fname in files:
                if fname.endswith(".md") and fname != ".gitkeep":
                    full = os.path.join(root, fname)
                    with open(full, encoding="utf-8") as f:
                        docs[full] = f.read()
    return docs


def build_backlinks() -> dict:
    docs = list_all_docs()
    backlinks: dict = {}
    for source_path, content in docs.items():
        for link in re.findall(r'\[\[(.+?)\]\]', content):
            backlinks.setdefault(link, []).append(source_path)
    return backlinks


def list_wiki_pages(dept: str) -> dict:
    dept_dir = os.path.join(KNOWLEDGE_DIR, dept)
    if not os.path.exists(dept_dir):
        return {}
    return {
        os.path.splitext(f)[0]: open(os.path.join(dept_dir, f), encoding="utf-8").read()
        for f in os.listdir(dept_dir)
        if f.endswith(".md") and f != ".gitkeep"
    }


def save_wiki_page(dept: str, page_name: str, content: str) -> None:
    path = os.path.join(KNOWLEDGE_DIR, dept, f"{page_name}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def upsert_doc(doc_id: str, content: str) -> None:
    _col.upsert(ids=[doc_id], documents=[content[:8000]])


def chroma_search(query: str, n_results: int = 5) -> dict:
    count = _col.count()
    if count == 0:
        return {}
    results = _col.query(query_texts=[query], n_results=min(n_results, count))
    return dict(zip(results["ids"][0], results["documents"][0]))


def seed_from_repo(repo_url: str) -> int:
    import shutil, subprocess, tempfile
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", "--depth=1", repo_url, tmp],
                       check=True, capture_output=True)
        ids, docs = [], []
        for root, _, files in os.walk(tmp):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(root, fname), tmp).replace("\\", "/")
                if rel.startswith("."):
                    continue
                content = open(os.path.join(root, fname), encoding="utf-8", errors="ignore").read()
                ids.append(f"agency:{rel}")
                docs.append(content[:8000])
        if ids:
            _col.upsert(ids=ids, documents=docs)
        return len(ids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def index_all_docs() -> int:
    docs = list_all_docs()
    if not docs:
        return 0
    _col.upsert(ids=list(docs.keys()), documents=[v[:8000] for v in docs.values()])
    return len(docs)


def append_log(dept: str, entry: str) -> None:
    path = os.path.join(KNOWLEDGE_DIR, dept, "log.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n## {date.today().isoformat()}\n{entry}\n")


def delete_doc(doc_id: str) -> None:
    path = Path(doc_id)
    if path.exists():
        path.unlink()
    try:
        _col.delete(ids=[doc_id])
    except Exception:
        pass


def get_doc_meta(doc_id: str) -> dict:
    path = Path(doc_id)
    parts = doc_id.replace("\\", "/").split("/")
    dept = parts[1] if len(parts) > 1 else ""
    doc_type = parts[-1].replace(".md", "") if parts else ""
    updated_at = (
        date.fromtimestamp(path.stat().st_mtime).isoformat()
        if path.exists() else ""
    )
    return {
        "id": doc_id,
        "title": path.stem,
        "dept": dept,
        "type": doc_type,
        "updated_at": updated_at,
        "size": path.stat().st_size if path.exists() else 0,
    }


def list_docs_meta() -> list:
    docs = list_all_docs()
    return [get_doc_meta(p) for p in docs]


def get_graph_data() -> dict:
    docs = list_all_docs()
    node_ids = set(docs.keys())
    nodes = []
    edges = []
    for path in node_ids:
        norm = path.replace("\\", "/")
        if norm.startswith("knowledge"):
            group = "knowledge"
        elif norm.startswith("meetings"):
            group = "meetings"
        else:
            group = "agency"
        nodes.append({
            "id": path,
            "label": os.path.basename(path).replace(".md", ""),
            "group": group,
            "title": norm,
        })
    for source_path, content in docs.items():
        for link in re.findall(r'\[\[(.+?)\]\]', content):
            target = os.path.join(KNOWLEDGE_DIR, *link.split("/")) + ".md"
            if target in node_ids:
                edges.append({"from": source_path, "to": target})
    return {"nodes": nodes, "edges": edges}


def render_graph() -> str:
    docs = list_all_docs()
    net = Network(height="500px", width="100%", bgcolor="#1a1a2e", font_color="white")
    net.barnes_hut()

    node_ids = set(docs.keys())
    for path in node_ids:
        label = os.path.basename(path).replace(".md", "")
        net.add_node(path, label=label, title=path.replace("\\", "/"))

    for source_path, content in docs.items():
        for link in re.findall(r'\[\[(.+?)\]\]', content):
            target = os.path.join(KNOWLEDGE_DIR, *link.split("/")) + ".md"
            if target in node_ids:
                net.add_edge(source_path, target)

    tmp = tempfile.mktemp(suffix=".html")
    net.write_html(tmp)
    with open(tmp, encoding="utf-8") as f:
        html = f.read()
    os.unlink(tmp)
    # ponytail: iframe data-URI bypasses Gradio's innerHTML script-blocking
    b64 = base64.b64encode(html.encode()).decode()
    return f'<iframe src="data:text/html;base64,{b64}" width="100%" height="520px" style="border:none;"></iframe>'
