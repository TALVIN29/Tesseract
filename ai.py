import json
import requests
from openai import OpenAI

OPENAI_API_KEY = "sk-YOUR-KEY-HERE"  # ponytail: hardcoded per user request — replace before running

client = OpenAI(api_key=OPENAI_API_KEY)


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
                    "Cite sources by file path."
                ),
            },
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return resp.choices[0].message.content


def generate(prompt: str, context: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at writing company SOPs and cultural documents in markdown. "
                    "Write clearly and concisely. Use headers, bullet points, numbered lists."
                ),
            },
            {
                "role": "user",
                "content": f"Context from existing docs:\n{context}\n\nWrite: {prompt}",
            },
        ],
    )
    return resp.choices[0].message.content


def search_github_sops(dept: str, industry: str) -> list:
    query = f"SOP {dept} {industry} in:file language:markdown"
    resp = requests.get(
        "https://api.github.com/search/code",
        params={"q": query, "per_page": 5},
        headers={"Accept": "application/vnd.github.v3+json"},
        timeout=10,
    )
    if resp.status_code != 200:
        return []
    items = resp.json().get("items", [])
    return [
        {
            "repo": item["repository"]["full_name"],
            "path": item["path"],
            "raw_url": (
                f"https://raw.githubusercontent.com/"
                f"{item['repository']['full_name']}/"
                f"{item['repository'].get('default_branch', 'main')}/"
                f"{item['path']}"
            ),
        }
        for item in items[:3]
    ]


def fetch_github_content(raw_url: str) -> str:
    resp = requests.get(raw_url, timeout=10)
    if resp.status_code != 200:
        return ""
    # ponytail: cap at 3000 chars per example — keeps adapt_sop context manageable
    return resp.text[:3000]


def adapt_sop(examples: list, company: dict) -> str:
    examples_text = "\n\n---\n\n".join(examples) if examples else "No examples found."
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at writing company SOPs. "
                    "Adapt the provided examples into a personalized SOP for the given company. "
                    "Output clean, well-structured markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Company: {company['name']}\n"
                    f"Department: {company['dept']}\n"
                    f"Industry: {company['industry']}\n\n"
                    f"Reference examples from GitHub:\n{examples_text}\n\n"
                    f"Write a personalized skill.md for this company's {company['dept']} department."
                ),
            },
        ],
    )
    return resp.choices[0].message.content
