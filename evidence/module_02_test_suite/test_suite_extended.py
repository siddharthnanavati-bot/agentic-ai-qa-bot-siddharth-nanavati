"""
Extended Test Suite Generated and Repaired by Agent (Module 2)
Runs green under pytest.
"""
import time
import json
import pytest
from agent.memory import ConversationMemory
from agent.tools import ToolRegistry, _is_safe_ast


def test_memory_ttl_pruning(tmp_path):
    store_file = tmp_path / "test_store.json"
    mem = ConversationMemory(session_id="s1", store_path=store_file, ttl=1)
    mem.add("user", "Hello world")
    assert len(mem.get_turns()) == 1

    # Simulate passage of time beyond TTL
    time.sleep(1.2)
    # Reloading memory should trigger pruning of expired sessions
    mem2 = ConversationMemory(session_id="s1", store_path=store_file, ttl=1)
    assert len(mem2.get_turns()) == 0


def test_sandbox_ast_validation_dangerous_builtins():
    unsafe_codes = [
        "import os",
        "from sys import exit",
        "eval('2 + 2')",
        "exec('print(1)')",
        "open('test.txt', 'w')",
    ]
    for code in unsafe_codes:
        safe, reason = _is_safe_ast(code)
        assert safe is False, f"Expected unsafe for: {code}"
        assert len(reason) > 0


def test_write_file_blocks_absolute_and_traversal_paths():
    bad_filenames = ["/etc/passwd", "C:\\boot.ini", "../test.txt", "..\\test.txt"]
    for fn in bad_filenames:
        res = json.loads(ToolRegistry.call("write_file", filename=fn, content="data"))
        assert "error" in res
        assert "Path traversal" in res["error"]
