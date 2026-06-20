"""
Live API tests for ai.py — requires a valid OPENAI_API_KEY in ai.py.
Run once to verify: python tests/test_ai.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ai

SAMPLE_NOTES = """
Engineering standup 2026-06-21.
John will fix the auth bug by Friday.
We decided to move session storage to Redis.
Mobile support is deferred until Q3.
Sarah needs to update the Redis config by tomorrow.
"""


def test_classify_returns_dept_and_type():
    result = ai.classify(SAMPLE_NOTES)
    assert "dept" in result, f"Missing 'dept' key: {result}"
    assert "type" in result, f"Missing 'type' key: {result}"
    assert result["dept"] in ("engineering", "hr"), f"Unknown dept: {result['dept']}"
    print(f"  classify result: {result}")


def test_extract_returns_list_with_action():
    items = ai.extract(SAMPLE_NOTES)
    assert isinstance(items, list), f"Expected list, got {type(items)}"
    assert len(items) > 0, "Expected at least one extracted item"
    categories = {i["category"] for i in items}
    assert "ACTION" in categories, f"Expected ACTION category, got: {categories}"
    print(f"  extract returned {len(items)} items: {[i['category'] for i in items]}")


def test_extract_item_has_required_keys():
    items = ai.extract(SAMPLE_NOTES)
    for item in items:
        assert "category" in item, f"Missing 'category': {item}"
        assert "what" in item, f"Missing 'what': {item}"


def test_search_returns_string():
    docs = {
        "knowledge/engineering/skill.md": "## Escalation\n1. Try for 2h\n2. Page tech lead"
    }
    result = ai.search("what is the escalation procedure?", docs)
    assert isinstance(result, str)
    assert len(result) > 10
    print(f"  search returned {len(result)} chars")


def test_generate_returns_markdown():
    result = ai.generate(
        "Write a short SOP for daily standups",
        "Context: Engineering team, 5 people, 15-min standup",
    )
    assert isinstance(result, str)
    assert len(result) > 50
    print(f"  generate returned {len(result)} chars")


if __name__ == "__main__":
    print("Running ai.py tests (live API calls)...")
    test_classify_returns_dept_and_type()
    print("classify: OK")
    test_extract_returns_list_with_action()
    test_extract_item_has_required_keys()
    print("extract: OK")
    test_search_returns_string()
    print("search: OK")
    test_generate_returns_markdown()
    print("generate: OK")
    print("\nAll ai tests passed.")
