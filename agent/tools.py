"""
Module: tools.py
Purpose: Tool registry and built-in tool implementations.
Evidence: Module 4 - Agent Fundamentals and Patterns.
"""
from __future__ import annotations

import ast
import io
import json
import pathlib
import re
import textwrap
import traceback
import urllib.request
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Any, Callable

CORPUS_DIR = pathlib.Path("corpus/sample_docs")
OUTPUT_DIR = pathlib.Path("agent_output")
OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    permissions: list[str]
    fn: Callable[..., str]


class ToolRegistry:
    _tools: dict[str, ToolSpec] = {}

    @classmethod
    def register(
        cls,
        name: str,
        description: str,
        parameters: dict[str, Any],
        permissions: list[str],
    ) -> Callable:
        def decorator(fn: Callable) -> Callable:
            cls._tools[name] = ToolSpec(
                name=name,
                description=description,
                parameters=parameters,
                permissions=permissions,
                fn=fn,
            )
            return fn
        return decorator

    @classmethod
    def get(cls, name: str) -> ToolSpec | None:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "permissions": t.permissions,
            }
            for t in cls._tools.values()
        ]

    @classmethod
    def call(cls, name: str, **kwargs: Any) -> str:
        spec = cls.get(name)
        if spec is None:
            raise ValueError(f"Unknown tool: '{name}'. Available: {list(cls._tools)}")
        return spec.fn(**kwargs)


@ToolRegistry.register(
    name="search_corpus",
    description=(
        "Full-text keyword search over the local document corpus. "
        "Returns top-k matching passages with doc IDs and relevance scores."
    ),
    parameters={
        "query": {"type": "string", "description": "Search keywords or phrase."},
        "top_k": {"type": "integer", "description": "Max results (default 3).", "default": 3},
    },
    permissions=["read"],
)
def search_corpus(query: str, top_k: int = 3) -> str:
    if not CORPUS_DIR.exists():
        return json.dumps({"error": f"Corpus directory not found: {CORPUS_DIR}"})

    docs = list(CORPUS_DIR.glob("*.md")) + list(CORPUS_DIR.glob("*.txt"))
    if not docs:
        return json.dumps({"results": [], "note": "Corpus is empty."})

    query_terms = set(re.findall(r"\w+", query.lower()))
    scored: list[tuple[float, str, str, str]] = []

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8", errors="ignore")
        words = set(re.findall(r"\w+", text.lower()))
        overlap = len(query_terms & words)
        if overlap == 0:
            continue
        score = overlap / max(len(query_terms), 1)
        # Extract full matching paragraph or first 1000 chars
        paragraphs = text.split("\n\n")
        matching_paras = [p.strip() for p in paragraphs if any(t in p.lower() for t in query_terms)]
        if matching_paras:
            snippet = " ".join(matching_paras)[:1000]
        else:
            snippet = text[:1000].strip()
        title = doc_path.stem.replace("_", " ").title()
        scored.append((round(score, 4), doc_path.stem, title, snippet))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [
        {"doc_id": doc_id, "title": title, "snippet": snippet, "score": score}
        for score, doc_id, title, snippet in scored[:top_k]
    ]
    return json.dumps({"results": results})


_ALLOWED_SCHEMES = {"http", "https"}
_TIMEOUT_SECONDS = 8


@ToolRegistry.register(
    name="fetch_url",
    description=(
        "Fetch a public HTTP/HTTPS URL and return text content (truncated to 3000 chars)."
    ),
    parameters={
        "url": {"type": "string", "description": "The URL to fetch."},
    },
    permissions=["network"],
)
def fetch_url(url: str) -> str:
    scheme = url.split("://")[0].lower() if "://" in url else ""
    if scheme not in _ALLOWED_SCHEMES:
        return json.dumps({"error": f"Scheme '{scheme}' not allowed. Use http or https."})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agentic-qa-agent/1.0"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            raw = resp.read(8192).decode("utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s{2,}", " ", text).strip()[:3000]
        return json.dumps({"url": url, "content": text})
    except Exception as exc:
        return json.dumps({"error": str(exc), "url": url})


_FORBIDDEN_BUILTINS = {"__import__", "eval", "exec", "open", "compile"}


def _is_safe_ast(code: str) -> tuple[bool, str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return False, "Import statements are not allowed in sandboxed code."
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in _FORBIDDEN_BUILTINS:
                return False, f"Call to '{name}' is not allowed."
    return True, ""


SAFE_BUILTINS = {
    "print": print,
    "range": range,
    "len": len,
    "int": int,
    "float": float,
    "str": str,
    "dict": dict,
    "list": list,
    "set": set,
    "tuple": tuple,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "bool": bool,
}


@ToolRegistry.register(
    name="run_code",
    description=(
        "Execute a short, sandboxed Python snippet (no imports, no file I/O). "
        "Returns stdout and stderr."
    ),
    parameters={
        "code": {"type": "string", "description": "Python code to execute (no imports)."},
    },
    permissions=["compute"],
)
def run_code(code: str) -> str:
    safe, reason = _is_safe_ast(code)
    if not safe:
        return json.dumps({"error": f"Code rejected by sandbox: {reason}"})

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    local_ns: dict = {}
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(textwrap.dedent(code), {"__builtins__": SAFE_BUILTINS}, local_ns)
    except Exception:
        stderr_buf.write(traceback.format_exc())

    return json.dumps({
        "stdout": stdout_buf.getvalue()[:2000],
        "stderr": stderr_buf.getvalue()[:500],
    })


@ToolRegistry.register(
    name="write_file",
    description=(
        "Write text content to a file inside the designated agent_output/ directory. "
        "Path traversal is blocked."
    ),
    parameters={
        "filename": {"type": "string", "description": "Filename only (no path separators)."},
        "content": {"type": "string", "description": "Text content to write."},
    },
    permissions=["write"],
)
def write_file(filename: str, content: str) -> str:
    if any(c in filename for c in ("/", "\\", "..")) or pathlib.Path(filename).is_absolute():
        return json.dumps({"error": "Path traversal detected - filename must be a bare name."})
    target = OUTPUT_DIR / filename
    target.write_text(content, encoding="utf-8")
    return json.dumps({"written_to": str(target.resolve()), "bytes": len(content)})
