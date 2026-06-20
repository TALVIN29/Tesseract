import os
import re
import tempfile
from datetime import date
from pyvis.network import Network

KNOWLEDGE_DIR = "knowledge"
MEETINGS_DIR = "meetings"


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

    # ponytail: write to temp file — pyvis write_html is more reliable than generate_html
    tmp = tempfile.mktemp(suffix=".html")
    net.write_html(tmp)
    with open(tmp, encoding="utf-8") as f:
        html = f.read()
    os.unlink(tmp)
    return html
