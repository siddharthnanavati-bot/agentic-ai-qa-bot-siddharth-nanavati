# Orchestration, MCP Pause/Resume & A2A Handoff (Module 9)

## 1. Paused-and-Resumed MCP Action
The system integrates an asynchronous Model Context Protocol (MCP) checkpointing pattern implemented in `orchestration/mcp_action.py`.

### Execution Trace:
1. **Initial Trigger:** Agent initiates a privileged action (`write_audit_log`).
2. **State Suspension:**
   ```
   [Workflow task_mcp_001] Step 1 complete. Status: PAUSED_WAITING_APPROVAL.
   Checkpoint persisted to: .mcp_checkpoint.json
   ```
3. **External Operator Intervention:** The system holds memory state safely on disk without consuming compute.
4. **Resumption:**
   ```
   [Workflow task_mcp_001] Operator approval received. Resuming execution from Step 2.
   Result: COMPLETED - Successfully wrote 26 bytes to audit_log.txt
   ```

---

## 2. Agent-to-Agent (A2A) Contract & Failed-Handoff Trace
The canonical A2A contract schema and failure trace is defined in `orchestration/a2a_contract.json`.

### Failed Handoff Trace Summary:
- **Sender:** `ResearchCoordinatorAgent`
- **Recipient:** `DataAnalysisSubagent`
- **Error Trigger:** The coordinator agent omitted the mandatory `trace_id` in `session_context` and exceeded the SLA timeout policy (sent `180s`, contract ceiling is `120s`).
- **Protocol Defense:** The receiving agent rejected the malformed delegation envelope with HTTP 422 `ContractViolationException`.
- **Self-Healing Resolution:** The coordinator agent trapped the rejection, re-serialized the envelope conforming strictly to the JSON schema, and successfully completed the delegation.
