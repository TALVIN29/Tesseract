import json
from datetime import date

import gradio as gr

from ai import classify, extract, search, generate, search_github_sops, fetch_github_content, adapt_sop
from store import read_knowledge, append_knowledge, save_meeting, list_all_docs, build_backlinks, render_graph

DEPARTMENTS = ["engineering", "hr"]
DOC_TYPES = ["skill", "soul"]


# ── Ingest ──────────────────────────────────────────────────────────────────

def ingest_notes(raw_text: str):
    if not raw_text.strip():
        return "Paste meeting notes first.", "", ""

    classification = classify(raw_text)
    dept = classification.get("dept", "engineering")
    meeting_type = classification.get("type", "standup")

    items = extract(raw_text)

    lines = [f"# {dept.title()} {meeting_type.title()} — {date.today().isoformat()}\n"]

    actions = [i for i in items if i.get("category") == "ACTION"]
    decisions = [i for i in items if i.get("category") == "DECIDED"]
    deferred = [i for i in items if i.get("category") == "DEFERRED"]

    if actions:
        lines.append("## Actions")
        for a in actions:
            lines.append(f"- ACTION | {a.get('owner', '?')} | {a.get('what', '?')} | {a.get('deadline') or 'TBD'}")
    if decisions:
        lines.append("\n## Decisions")
        for d in decisions:
            lines.append(f"- DECIDED: {d.get('what', '?')}")
    if deferred:
        lines.append("\n## Deferred")
        for d in deferred:
            lines.append(f"- DEFERRED: {d.get('what', '?')} → {d.get('deadline') or 'TBD'}")

    record = "\n".join(lines)
    path = save_meeting(dept, record)

    summary = f"**Dept:** {dept} | **Type:** {meeting_type}\n**Saved to:** `{path}`"
    return summary, record, json.dumps(items, indent=2)


# ── Hub ──────────────────────────────────────────────────────────────────────

def view_hub(dept: str, doc_type: str):
    content = read_knowledge(dept, doc_type)
    backlinks = build_backlinks()
    key = f"{dept}/{doc_type}"
    linked_from = backlinks.get(key, [])
    if linked_from:
        content += "\n\n---\n\n**Linked from:** " + ", ".join(f"`{p}`" for p in linked_from)
    return content


# ── Search ───────────────────────────────────────────────────────────────────

def search_hub(query: str):
    if not query.strip():
        return "Enter a question."
    docs = list_all_docs()
    if not docs:
        return "Knowledge base is empty. Ingest some notes first."
    return search(query, docs)


# ── Generate ─────────────────────────────────────────────────────────────────

def github_bootstrap(dept: str, industry: str, company_name: str):
    results = search_github_sops(dept, industry)
    if not results:
        context = read_knowledge(dept, "skill")
        adapted = generate(
            f"Write a complete skill.md SOP for {company_name}'s {dept} department in the {industry} industry.",
            context,
        )
        return "No GitHub results found — generated from internal context instead.", adapted

    examples = [fetch_github_content(r["raw_url"]) for r in results]
    examples = [e for e in examples if e]

    company = {"name": company_name or "Acme Corp", "dept": dept, "industry": industry}
    adapted = adapt_sop(examples, company)

    sources = "\n".join(f"- [{r['repo']}]({r['raw_url']}) `{r['path']}`" for r in results)
    return f"**GitHub sources used:**\n{sources}", adapted


def confirm_append(dept: str, doc_type: str, content: str):
    if not content.strip():
        return "Nothing to append — generate content first."
    append_knowledge(dept, doc_type, content)
    return f"Appended to `knowledge/{dept}/{doc_type}.md`"


# ── Graph ─────────────────────────────────────────────────────────────────────

def show_graph():
    return render_graph()


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Tesseract Knowledge Hub") as app:
    gr.Markdown("# Tesseract Knowledge Hub\n*Internal knowledge, structured by AI.*")

    with gr.Tab("Ingest"):
        gr.Markdown("Paste raw meeting notes — AI classifies and extracts structured items.")
        notes_input = gr.Textbox(lines=8, placeholder="Paste meeting notes here...")
        ingest_btn = gr.Button("Process Notes", variant="primary")
        ingest_summary = gr.Markdown()
        ingest_record = gr.Textbox(label="Saved Record (markdown)", lines=10)
        ingest_items = gr.Textbox(label="Extracted Items (JSON)", lines=8)
        ingest_btn.click(
            ingest_notes,
            inputs=notes_input,
            outputs=[ingest_summary, ingest_record, ingest_items],
        )

    with gr.Tab("Hub"):
        gr.Markdown("Browse department knowledge: **skill.md** (HOW) and **soul.md** (WHY).")
        with gr.Row():
            hub_dept = gr.Dropdown(DEPARTMENTS, value="engineering", label="Department")
            hub_doc = gr.Dropdown(DOC_TYPES, value="skill", label="Document")
        hub_btn = gr.Button("View")
        hub_content = gr.Markdown()
        hub_btn.click(view_hub, inputs=[hub_dept, hub_doc], outputs=hub_content)

    with gr.Tab("Search"):
        gr.Markdown("Ask a question — AI searches all knowledge and meeting records.")
        search_input = gr.Textbox(placeholder="What's our escalation procedure?")
        search_btn = gr.Button("Search", variant="primary")
        search_output = gr.Markdown()
        search_btn.click(search_hub, inputs=search_input, outputs=search_output)

    with gr.Tab("Generate"):
        gr.Markdown(
            "Bootstrap a **skill.md** from real GitHub SOP examples, adapted to your company."
        )
        with gr.Row():
            gen_dept = gr.Dropdown(DEPARTMENTS, value="engineering", label="Department")
            gen_industry = gr.Textbox(value="fintech", label="Industry")
            gen_company = gr.Textbox(value="Acme Corp", label="Company Name")
        gen_btn = gr.Button("Search GitHub + Generate", variant="primary")
        gen_sources = gr.Markdown()
        gen_content = gr.Textbox(
            label="Generated Content (edit before saving)", lines=20
        )
        with gr.Row():
            gen_doc_type = gr.Dropdown(DOC_TYPES, value="skill", label="Append to")
            confirm_btn = gr.Button("Confirm & Append", variant="secondary")
        confirm_output = gr.Markdown()
        gen_btn.click(
            github_bootstrap,
            inputs=[gen_dept, gen_industry, gen_company],
            outputs=[gen_sources, gen_content],
        )
        confirm_btn.click(
            confirm_append,
            inputs=[gen_dept, gen_doc_type, gen_content],
            outputs=confirm_output,
        )

    with gr.Tab("Graph"):
        gr.Markdown(
            "Knowledge graph — nodes are docs, edges are `[[links]]`. Click **Render** after ingesting notes."
        )
        graph_btn = gr.Button("Render Graph")
        graph_output = gr.HTML()
        graph_btn.click(show_graph, outputs=graph_output)


if __name__ == "__main__":
    app.launch(theme=gr.themes.Soft())
