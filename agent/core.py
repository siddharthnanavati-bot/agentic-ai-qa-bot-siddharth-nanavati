"""
Module: core.py
Purpose: ReAct agent loop with tool dispatch, retry/fallback on tool failure,
         guardrail integration, and conversation memory.
Evidence: Module 4 - Agent Fundamentals and Patterns.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from typing import Any

from .guardrails import GuardrailPipeline
from .memory import ConversationMemory
from .structured_output import build_answer, AnswerModel, STRUCTURED_OUTPUT_SYSTEM_PROMPT
from .tools import ToolRegistry

logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
MAX_ITERATIONS = 6
MAX_TOOL_RETRIES = 2
TIMEOUT_SECONDS = 2

_OLLAMA_ONLINE: bool | None = None


def _call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    global _OLLAMA_ONLINE
    if _OLLAMA_ONLINE is False:
        raise RuntimeError("Ollama previously unreachable - using deterministic engine.")

    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode())
            _OLLAMA_ONLINE = True
            return data.get("response", "")
    except Exception as exc:
        _OLLAMA_ONLINE = False
        raise RuntimeError(f"Ollama call failed: {exc}") from exc


SYSTEM_PROMPT = """\
You are a Grounded Research & QA Agent. You answer questions ONLY using evidence
from your tools. Never fabricate facts. When you have enough information, produce
a final structured JSON answer.

You must respond in one of two formats:

FORMAT A - when you need to call a tool:
THOUGHT: <your reasoning>
ACTION: <tool_name>
ACTION_INPUT: <JSON object matching the tool's parameters>

FORMAT B - when you have a final answer:
THOUGHT: <final reasoning>
FINAL_ANSWER: <JSON matching the AnswerModel schema>

Available tools:
{tool_list}

{structured_schema}
"""


def _build_prompt(memory: ConversationMemory, query: str) -> str:
    tool_list = json.dumps(ToolRegistry.list_tools(), indent=2)
    history = ""
    for turn in memory.get_turns():
        prefix = turn["role"].upper()
        history += f"{prefix}: {turn['content']}\n\n"
    return (
        SYSTEM_PROMPT.format(
            tool_list=tool_list,
            structured_schema=STRUCTURED_OUTPUT_SYSTEM_PROMPT,
        )
        + "\n\n"
        + history
        + f"USER: {query}\n\nASSISTANT:"
    )


def _parse_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if "FINAL_ANSWER:" in text:
        raw = text.split("FINAL_ANSWER:", 1)[1].strip()
        return {"type": "answer", "raw": raw}
    if "ACTION:" in text and "ACTION_INPUT:" in text:
        try:
            tool = text.split("ACTION:", 1)[1].split("\n")[0].strip()
            args_raw = text.split("ACTION_INPUT:", 1)[1].strip()
            start = args_raw.find("{")
            end = args_raw.rfind("}") + 1
            args = json.loads(args_raw[start:end]) if start != -1 else {}
            return {"type": "action", "tool": tool, "args": args}
        except (json.JSONDecodeError, IndexError):
            pass
    return {"type": "unknown", "raw": text}


class Agent:
    def __init__(
        self,
        session_id: str = "default",
        model: str = DEFAULT_MODEL,
        guardrails: GuardrailPipeline | None = None,
    ) -> None:
        self.session_id = session_id
        self.model = model
        self.memory = ConversationMemory(session_id)
        self.guardrails = guardrails or GuardrailPipeline.default()

    def run(self, query: str) -> dict[str, Any]:
        t0 = time.time()

        # Input guardrail check
        input_check = self.guardrails.check_input(query)
        if not input_check.passed:
            logger.warning("Input blocked: %s", input_check.reason)
            return {
                "answer": None,
                "blocked": True,
                "block_reason": input_check.reason,
                "iterations": 0,
                "tool_calls": [],
                "elapsed_s": round(time.time() - t0, 3),
            }

        self.memory.add("user", query)
        tool_calls: list[dict] = []
        answer_model: AnswerModel | None = None
        raw_output: str = ""

        for iteration in range(1, MAX_ITERATIONS + 1):
            prompt = _build_prompt(self.memory, query if iteration == 1 else "")
            try:
                raw = _call_ollama(prompt, self.model)
            except Exception as exc:
                logger.info("Ollama offline or call error (%s). Using deterministic grounded fallback.", exc)
                # Fallback: perform search directly and formulate grounded answer
                search_res_json = ToolRegistry.call("search_corpus", query=query, top_k=2)
                tool_calls.append({"tool": "search_corpus", "args": {"query": query, "top_k": 2}, "observation": search_res_json})
                parsed_res = json.loads(search_res_json)
                results = parsed_res.get("results", [])
                if results:
                    best = results[0]
                    ans_text = f"Based on {best['title']}, {best['snippet']}"
                    sources = [{"doc_id": best["doc_id"], "title": best["title"], "snippet": best["snippet"], "score": best["score"]}]
                    is_gr = True
                else:
                    ans_text = "No direct corpus matches found."
                    sources = []
                    is_gr = False

                fallback_payload = {
                    "answer": ans_text,
                    "confidence": 0.85 if is_gr else 0.2,
                    "sources": sources,
                    "reasoning_steps": ["Queried local corpus via search_corpus tool", "Grounded response in top retrieved document"],
                    "is_grounded": is_gr,
                    "out_of_domain": False
                }
                raw = "FINAL_ANSWER: " + json.dumps(fallback_payload)

            parsed = _parse_response(raw)

            if parsed["type"] == "action":
                tool_name = parsed["tool"]
                args = parsed["args"]
                observation = self._call_tool_with_retry(tool_name, args)
                tool_calls.append({"tool": tool_name, "args": args, "observation": observation})
                self.memory.add("assistant", f"ACTION: {tool_name}\nACTION_INPUT: {json.dumps(args)}")
                self.memory.add("tool", f"OBSERVATION: {observation}")

            elif parsed["type"] == "answer":
                raw_output = parsed["raw"]
                output_check = self.guardrails.check_output(raw_output)
                if not output_check.passed:
                    logger.warning("Output blocked: %s", output_check.reason)
                    return {
                        "answer": None,
                        "blocked": True,
                        "block_reason": output_check.reason,
                        "iterations": iteration,
                        "tool_calls": tool_calls,
                        "elapsed_s": round(time.time() - t0, 3),
                    }
                try:
                    answer_model = build_answer(raw_output, query)
                except Exception as exc:
                    logger.warning("Structured output parse fallback: %s", exc)
                    answer_model = None
                self.memory.add("assistant", raw_output)
                break
            else:
                self.memory.add("assistant", raw[:500])
                break

        return {
            "answer": answer_model.model_dump() if answer_model else {"raw": raw_output or raw},
            "blocked": False,
            "block_reason": "",
            "iterations": iteration,
            "tool_calls": tool_calls,
            "elapsed_s": round(time.time() - t0, 3),
        }

    def _call_tool_with_retry(self, tool_name: str, args: dict) -> str:
        for attempt in range(1, MAX_TOOL_RETRIES + 2):
            try:
                result = ToolRegistry.call(tool_name, **args)
                return result
            except Exception as exc:
                if attempt > MAX_TOOL_RETRIES:
                    return json.dumps({
                        "error": f"Tool '{tool_name}' failed after {attempt} attempts: {exc}",
                        "suggestion": "Try an alternative query or tool.",
                    })
                time.sleep(0.3 * attempt)
        return json.dumps({"error": "Tool retry failed."})
