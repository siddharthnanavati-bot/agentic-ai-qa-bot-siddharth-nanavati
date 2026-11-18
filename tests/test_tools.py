import json
from agent.tools import ToolRegistry


def test_search_corpus_finds_document():
    res_str = ToolRegistry.call("search_corpus", query="agentic testing determinism", top_k=2)
    data = json.loads(res_str)
    assert "results" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["doc_id"] == "doc_01_agentic_testing"


def test_run_code_sandbox_safety():
    # Safe code
    res_safe = json.loads(ToolRegistry.call("run_code", code="x = 10 + 20\nprint(x)"))
    assert "30" in res_safe["stdout"]

    # Blocked import
    res_unsafe = json.loads(ToolRegistry.call("run_code", code="import os; os.system('ls')"))
    assert "error" in res_unsafe
    assert "Import statements are not allowed" in res_unsafe["error"]


def test_write_file_path_traversal():
    res = json.loads(ToolRegistry.call("write_file", filename="../secret.txt", content="payload"))
    assert "error" in res
    assert "Path traversal" in res["error"]
