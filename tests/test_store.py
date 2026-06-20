import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import store

_orig_knowledge = store.KNOWLEDGE_DIR
_orig_meetings = store.MEETINGS_DIR


def setup_tmp():
    tmp = tempfile.mkdtemp()
    store.KNOWLEDGE_DIR = os.path.join(tmp, "knowledge")
    store.MEETINGS_DIR = os.path.join(tmp, "meetings")
    os.makedirs(os.path.join(store.KNOWLEDGE_DIR, "engineering"), exist_ok=True)
    with open(os.path.join(store.KNOWLEDGE_DIR, "engineering", "skill.md"), "w") as f:
        f.write("# Eng Skill\n\nDeploy steps here. See also: [[engineering/soul]]")
    with open(os.path.join(store.KNOWLEDGE_DIR, "engineering", "soul.md"), "w") as f:
        f.write("# Eng Soul\n\nQuality bar. See also: [[engineering/skill]]")
    return tmp


def teardown_tmp(tmp):
    store.KNOWLEDGE_DIR = _orig_knowledge
    store.MEETINGS_DIR = _orig_meetings
    shutil.rmtree(tmp)


def test_read_knowledge():
    tmp = setup_tmp()
    content = store.read_knowledge("engineering", "skill")
    assert "Deploy steps" in content, f"Expected 'Deploy steps' in: {content}"
    teardown_tmp(tmp)


def test_read_knowledge_missing():
    tmp = setup_tmp()
    result = store.read_knowledge("engineering", "nonexistent")
    assert "No nonexistent.md found" in result
    teardown_tmp(tmp)


def test_append_knowledge():
    tmp = setup_tmp()
    store.append_knowledge("engineering", "skill", "## New Section\nNew content.")
    content = store.read_knowledge("engineering", "skill")
    assert "New Section" in content
    teardown_tmp(tmp)


def test_save_meeting_creates_file():
    tmp = setup_tmp()
    path = store.save_meeting("engineering", "# Standup\n- ACTION | John | Fix bug | Friday")
    assert os.path.exists(path), f"Meeting file not found: {path}"
    with open(path) as f:
        assert "Fix bug" in f.read()
    teardown_tmp(tmp)


def test_save_meeting_appends_same_day():
    tmp = setup_tmp()
    store.save_meeting("engineering", "First entry")
    store.save_meeting("engineering", "Second entry")
    docs = store.list_all_docs()
    combined = " ".join(docs.values())
    assert "First entry" in combined
    assert "Second entry" in combined
    teardown_tmp(tmp)


def test_list_all_docs():
    tmp = setup_tmp()
    docs = store.list_all_docs()
    paths = list(docs.keys())
    assert any("skill.md" in p for p in paths)
    assert any("soul.md" in p for p in paths)
    teardown_tmp(tmp)


def test_build_backlinks():
    tmp = setup_tmp()
    backlinks = store.build_backlinks()
    # engineering/soul.md contains [[engineering/skill]]
    assert "engineering/skill" in backlinks, f"Expected 'engineering/skill' in backlinks: {list(backlinks.keys())}"
    # engineering/skill.md contains [[engineering/soul]]
    assert "engineering/soul" in backlinks
    teardown_tmp(tmp)


def test_render_graph_returns_html():
    tmp = setup_tmp()
    html = store.render_graph()
    assert "<html" in html.lower() or "<!doctype" in html.lower(), "Expected HTML output"
    teardown_tmp(tmp)


if __name__ == "__main__":
    test_read_knowledge()
    print("read_knowledge: OK")
    test_read_knowledge_missing()
    print("read_knowledge_missing: OK")
    test_append_knowledge()
    print("append_knowledge: OK")
    test_save_meeting_creates_file()
    print("save_meeting creates file: OK")
    test_save_meeting_appends_same_day()
    print("save_meeting appends same day: OK")
    test_list_all_docs()
    print("list_all_docs: OK")
    test_build_backlinks()
    print("build_backlinks: OK")
    test_render_graph_returns_html()
    print("render_graph: OK")
    print("\nAll store tests passed.")
