import base64
import json
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def classify(text: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    'Classify this meeting note. Return JSON only: '
                    '{"dept": "engineering" or "hr", "type": "standup|decision|retrospective|planning|incident"}'
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return json.loads(resp.choices[0].message.content)


def extract(text: str) -> list:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract structured items from meeting notes. "
                    'Return JSON: {"items": [{"category": "ACTION|DECIDED|DEFERRED", '
                    '"owner": "name or team", "what": "description", "deadline": "date string or null"}]}'
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("items", [])


def search(query: str, docs: dict) -> str:
    context = "\n\n".join(f"=== {path} ===\n{content}" for path, content in docs.items())
    # ponytail: cap context at 12000 chars — sufficient for POC file sizes
    context = context[:12000]
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a knowledge base assistant. "
                    "Answer using only the provided documents. "
                    "Cite sources by file path.\n\n"
                    "After your answer, add:\n"
                    "## Knowledge Gaps\n"
                    "List information that was absent, uncertain, or would improve this answer "
                    "if added to the knowledge base. Suggest specific doc titles or topics to ingest. "
                    "If no gaps, write \"None identified.\""
                ),
            },
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return resp.choices[0].message.content


def compile_to_wiki(new_content: str, dept: str, wiki_pages: dict) -> dict:
    pages_ctx = "\n\n".join(
        f"=== {name} ===\n{content[:1000]}" for name, content in wiki_pages.items()
    )[:8000]
    resp = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You maintain a markdown wiki for a company department. "
                    "Given new content, identify which wiki pages need updating and return their full updated markdown. "
                    "Preserve existing structure. Add cross-links using [[page_name]] syntax. "
                    'Return JSON: {"updates": [{"page": "page_name", "content": "full markdown"}]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Department: {dept}\n\n"
                    f"Current wiki pages:\n{pages_ctx}\n\n"
                    f"New content to compile:\n{new_content}"
                ),
            },
        ],
    )
    data = json.loads(resp.choices[0].message.content)
    return {u["page"]: u["content"] for u in data.get("updates", [])}


def lint_wiki(all_pages: dict) -> str:
    context = "\n\n".join(
        f"=== {name} ===\n{content[:500]}" for name, content in all_pages.items()
    )[:8000]
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Audit this markdown wiki. Find: orphaned pages (no incoming links), "
                    "contradictions between pages, stale or unverified claims, missing cross-references. "
                    "Return a markdown report with findings grouped by severity and suggested fixes."
                ),
            },
            {"role": "user", "content": f"Wiki pages:\n{context}"},
        ],
    )
    return resp.choices[0].message.content


def transcribe(file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = client.audio.transcriptions.create(model="whisper-1", file=f)
    return resp.text


def file_to_text_from_path(file_path: str) -> str:
    from pathlib import Path as _Path
    import pdfplumber
    ext = _Path(file_path).suffix.lower()
    if ext in {".mp3", ".mp4", ".wav", ".m4a", ".webm"}:
        return transcribe(file_path)
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return extract_from_image(file_path)
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return open(file_path, encoding="utf-8").read()


def extract_from_image(file_path: str) -> str:
    ext = Path(file_path).suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(ext, "jpeg")
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract all text and describe the content of this image for use as meeting notes."},
                {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{data}"}},
            ],
        }],
    )
    return resp.choices[0].message.content


