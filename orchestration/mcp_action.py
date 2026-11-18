"""
Module: mcp_action.py
Purpose: Demonstration of an asynchronous MCP action with Pause and Resume.
Evidence: Module 9 - Orchestration, Memory, Integration and Protocol Design.
"""
from __future__ import annotations

import json
import pathlib
import time
from dataclasses import asdict, dataclass


CHECKPOINT_PATH = pathlib.Path(".mcp_checkpoint.json")


@dataclass
class WorkflowState:
    task_id: str
    step: int
    query: str
    status: str
    action_pending: str
    payload: dict
    timestamp: float


def start_sensitive_workflow(task_id: str, query: str, file_target: str, data: str) -> dict:
    """Initiates an agent action that requires explicit human/MCP approval."""
    state = WorkflowState(
        task_id=task_id,
        step=1,
        query=query,
        status="PAUSED_WAITING_APPROVAL",
        action_pending="write_audit_log",
        payload={"target": file_target, "content": data},
        timestamp=time.time(),
    )
    # Checkpoint state to storage
    CHECKPOINT_PATH.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
    print(f"[Workflow {task_id}] Paused at step 1. Waiting for MCP approval.")
    return asdict(state)


def resume_workflow(task_id: str, approved: bool) -> dict:
    """Resumes the paused MCP workflow from the saved checkpoint."""
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError("No active MCP checkpoint found.")

    data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    if data["task_id"] != task_id:
        raise ValueError(f"Task ID mismatch: expected {data['task_id']}, got {task_id}")

    if not approved:
        data["status"] = "REJECTED_BY_OPERATOR"
        data["step"] = 2
        CHECKPOINT_PATH.unlink(missing_ok=True)
        print(f"[Workflow {task_id}] Execution resumed: Action REJECTED.")
        return data

    # Perform action upon resume
    data["status"] = "COMPLETED"
    data["step"] = 2
    data["result"] = f"Successfully wrote {len(data['payload']['content'])} bytes to {data['payload']['target']}"
    CHECKPOINT_PATH.unlink(missing_ok=True)
    print(f"[Workflow {task_id}] Execution resumed: Action EXECUTED successfully.")
    return data


if __name__ == "__main__":
    t_id = "task_mcp_001"
    paused = start_sensitive_workflow(t_id, "Archive report", "audit_log.txt", "Audit confirmation string")
    print("Checkpoint State:", paused["status"])
    resumed = resume_workflow(t_id, approved=True)
    print("Resumed Result:", resumed["status"], "-", resumed.get("result"))
