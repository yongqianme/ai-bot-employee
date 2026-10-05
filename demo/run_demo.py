#!/usr/bin/env python3
"""Offline orchestration demo for Universal AI Employee Builder.

This script intentionally performs NO live model calls and NO external sends.
It demonstrates the durable employee contract, authority gate, runtime adapter,
and task-ledger behavior with synthetic data.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Run: python -m pip install -r demo/requirements.txt", file=sys.stderr)
    raise SystemExit(2)

HERE = Path(__file__).resolve().parent
EMPLOYEE_DIR = HERE / "employee"
DEFAULT_PROSPECT = HERE / "sample-inputs" / "prospect.json"
OUTPUT_DIR = HERE / "output"

RUNTIME_NOTES = {
    "grok-bot": "Named Bot + skill; routine for recurring work; connectors/MCP for tools; preserve A3 approval gate.",
    "xai-api": "Grok reasoning/tool calls; host application owns durable state, scheduling, approvals, secrets, and ledger.",
    "openai": "Provider model/tool interface; host/runtime preserves the same contract, authority, state, and approval semantics.",
    "anthropic": "Provider model/tool interface; host/runtime preserves the same contract, authority, state, and approval semantics.",
    "gemini": "Provider model/tool interface; host/runtime preserves the same contract, authority, state, and approval semantics.",
    "local": "Local instruction-following model; host supplies tools/state/approvals; unavailable capabilities degrade to draft mode.",
}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_fields(data: dict, fields: list[str]) -> None:
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValueError("Missing required prospect fields: " + ", ".join(missing))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_brief(prospect: dict) -> str:
    return (
        f"Company: {prospect['company']}\n"
        f"Contact: {prospect['contact_name']} — {prospect['contact_role']}\n"
        f"Industry: {prospect.get('industry', 'not supplied')}\n"
        f"Verified demo signal: {prospect['signal']}\n"
        f"Provenance: {prospect['source']}\n"
    )


def build_draft(prospect: dict) -> str:
    return (
        f"Hi {prospect['contact_name']},\n\n"
        f"I noticed that {prospect['company']} is {prospect['signal'][0].lower() + prospect['signal'][1:]} "
        "That kind of expansion often creates operational coordination work across sites.\n\n"
        "Would a short conversation about how your team is approaching that rollout be useful?\n\n"
        "Best,\nDemo AI Employee\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the offline Universal AI Employee demo.")
    parser.add_argument(
        "--runtime",
        choices=sorted(RUNTIME_NOTES),
        default="grok-bot",
        help="Runtime adapter to illustrate (default: grok-bot).",
    )
    parser.add_argument(
        "--prospect",
        type=Path,
        default=DEFAULT_PROSPECT,
        help="Path to prospect JSON input.",
    )
    parser.add_argument(
        "--request-send",
        action="store_true",
        help="Request the A3 send step. Without approval, the task stops at waiting_approval.",
    )
    parser.add_argument(
        "--approve-send",
        action="store_true",
        help="Explicitly approve the demo A3 send. The send is still simulated; no external message is sent.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print the loaded employee contract and authority actions before running.",
    )
    args = parser.parse_args()

    if args.approve_send and not args.request_send:
        args.request_send = True

    contract = load_yaml(EMPLOYEE_DIR / "employee-contract.yaml")
    authority = load_yaml(EMPLOYEE_DIR / "authority-matrix.yaml")
    prospect = load_json(args.prospect)

    task_id = "demo-" + uuid.uuid4().hex[:10]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ledger = {
        "task_id": task_id,
        "timestamp": utc_now(),
        "trigger": "manual_cli",
        "requester": "repository user",
        "goal": "Research supplied prospect evidence, draft outreach, and optionally request an approved send.",
        "input_refs": [str(args.prospect)],
        "model": "offline-demo-no-model-call",
        "runtime": args.runtime,
        "actions": [],
        "approvals": [],
        "artifacts": [],
        "state_changes": [],
        "verification": {},
        "status": "running",
        "error": None,
        "usage": {"external_api_calls": 0, "real_messages_sent": 0},
        "next_action": None,
    }

    print(f"\n=== Universal AI Employee Demo ===")
    print(f"Employee: {contract['employee']['name']} — {contract['employee']['role']}")
    print(f"Runtime:  {args.runtime}")
    print(f"Adapter:  {RUNTIME_NOTES[args.runtime]}")
    print(f"Task ID:  {task_id}\n")

    if args.show_config:
        print("--- Authority actions ---")
        for action in authority.get("actions", []):
            print(f"{action['action']}: {action['class']} (approval_required={action['approval_required']})")
        print()

    try:
        print("[1/6] INTAKE    Load prospect task")
        require_fields(prospect, ["company", "contact_name", "contact_role", "signal", "source"])
        ledger["actions"].append({"action": "read_prospect_input", "class": "A0", "result": "ok"})

        print("[2/6] CONTEXT   Use only supplied, provenance-tagged evidence")
        brief = build_brief(prospect)
        brief_path = OUTPUT_DIR / f"{task_id}-prospect-brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        ledger["artifacts"].append(str(brief_path))
        ledger["actions"].append({"action": "create_prospect_brief", "class": "A1", "result": "ok"})

        print("[3/6] PLAN      Research -> draft -> approval gate -> simulated send")

        print("[4/6] EXECUTE   Create outreach draft (A1, no approval required)")
        draft = build_draft(prospect)
        draft_path = OUTPUT_DIR / f"{task_id}-outreach-draft.txt"
        draft_path.write_text(draft, encoding="utf-8")
        ledger["artifacts"].append(str(draft_path))
        ledger["actions"].append({"action": "draft_outreach", "class": "A1", "result": "ok"})

        if args.request_send:
            print("[5/6] AUTHORIZE Execute send_outreach (A3)")
            if not args.approve_send:
                print("      BLOCKED: explicit approval required. No message was sent.")
                ledger["approvals"].append({"action": "send_outreach", "required": True, "approved": False})
                ledger["status"] = "waiting_approval"
                ledger["verification"] = {
                    "brief_created": brief_path.exists(),
                    "draft_created": draft_path.exists(),
                    "real_message_sent": False,
                    "approval_gate_enforced": True,
                }
                ledger["next_action"] = "Obtain explicit approval, then resume the A3 send step."
            else:
                print("      APPROVED: performing SIMULATED send only.")
                simulated_id = "sim-msg-" + uuid.uuid4().hex[:8]
                ledger["approvals"].append({"action": "send_outreach", "required": True, "approved": True})
                ledger["actions"].append({
                    "action": "send_outreach",
                    "class": "A3",
                    "result": "simulated",
                    "message_id": simulated_id,
                    "note": "No external system was contacted.",
                })
                ledger["state_changes"].append(f"simulated outbound message recorded: {simulated_id}")
                ledger["status"] = "completed"
                ledger["verification"] = {
                    "brief_created": brief_path.exists(),
                    "draft_created": draft_path.exists(),
                    "real_message_sent": False,
                    "simulated_send_recorded": True,
                    "approval_gate_enforced": True,
                }
                ledger["next_action"] = None
        else:
            print("[5/6] AUTHORIZE No external send requested; remain in draft mode")
            ledger["status"] = "completed"
            ledger["verification"] = {
                "brief_created": brief_path.exists(),
                "draft_created": draft_path.exists(),
                "real_message_sent": False,
                "approval_gate_enforced": True,
            }
            ledger["next_action"] = "Human may review the draft or request an A3 send."

        print("[6/6] RECORD    Write normalized task ledger")

    except Exception as exc:
        ledger["status"] = "failed"
        ledger["error"] = str(exc)
        ledger["verification"] = {"real_message_sent": False}
        ledger["next_action"] = "Correct the input and retry."
        print(f"ERROR: {exc}", file=sys.stderr)

    ledger_path = OUTPUT_DIR / f"{task_id}-ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    print(f"\nStatus: {ledger['status']}")
    print(f"Ledger: {ledger_path}")
    print("\n--- Prospect brief ---")
    if 'brief' in locals():
        print(brief.rstrip())
    print("\n--- Outreach draft ---")
    if 'draft' in locals():
        print(draft.rstrip())
    print("\nNOTE: This demo never calls a live model or sends a real message.")

    return 0 if ledger["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
