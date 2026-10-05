# Demo: From Skill to AI Employee

This demo shows how to use the **Universal AI Employee Builder** as an operating contract rather than as a persona prompt.

The example employee is **Scout**, a fictional sales research and outreach assistant. The demo is intentionally offline: it performs no live model calls and sends no real messages. Its purpose is to make the control flow visible.

## What the demo proves

The same employee definition can be carried across runtimes while preserving the important behavior:

```text
prospect input
    ↓
A0 inspect evidence
    ↓
A1 create brief + outreach draft
    ↓
A3 send requested?
    ├── no  → complete in draft mode
    └── yes → approval gate
                 ├── no approval → waiting_approval
                 └── approved    → simulated send + verified ledger
```

The model/runtime can change. The employee contract, authority matrix, and audit semantics do not.

## Files

```text
demo/
├── README.md
├── requirements.txt
├── run_demo.py
├── sample-inputs/
│   └── prospect.json
├── employee/
│   ├── EMPLOYEE.md
│   ├── employee-contract.yaml
│   ├── authority-matrix.yaml
│   ├── tool-map.yaml
│   ├── memory-policy.md
│   ├── runtime-adapter.md
│   ├── task-ledger.schema.json
│   └── evals/
│       └── eval-cases.yaml
└── output/
```

## Run it

From the repository root:

```bash
python -m pip install -r demo/requirements.txt
```

### 1. Draft-only run

```bash
python demo/run_demo.py --runtime grok-bot
```

Expected behavior:

- loads the employee contract;
- loads the synthetic prospect input;
- creates a prospect brief;
- creates an outreach draft;
- performs no send;
- writes a task ledger under `demo/output/`.

### 2. Request a send without approval

```bash
python demo/run_demo.py --runtime grok-bot --request-send
```

Expected final state:

```text
waiting_approval
```

The `send_outreach` action is `A3`, so the employee stops before the side effect.

### 3. Explicitly approve the send

```bash
python demo/run_demo.py --runtime grok-bot --request-send --approve-send
```

The script records a **simulated** send and a synthetic message ID. It still does not contact an email provider.

### 4. Swap runtimes

Run the same employee with a different adapter label:

```bash
python demo/run_demo.py --runtime xai-api --request-send
python demo/run_demo.py --runtime openai --request-send
python demo/run_demo.py --runtime anthropic --request-send
python demo/run_demo.py --runtime gemini --request-send
python demo/run_demo.py --runtime local --request-send
```

The expected authority behavior is identical. This is the portability test: the runtime changes, but `A3` still requires approval.

Use `--show-config` to see the loaded authority actions:

```bash
python demo/run_demo.py --runtime grok-bot --show-config
```

## How this maps to Grok Bot

For a real Grok Bot deployment:

1. Create a named Bot for the employee role.
2. Turn the repeatable research/drafting procedure into a Bot **skill**.
3. Use a **routine** if the work should run on a schedule or event cadence.
4. Map research and business-system access to approved connectors or MCP tools.
5. Preserve the employee contract as the durable source of truth.
6. Keep `send_outreach` as an `A3` action and preserve explicit approval unless a deliberately narrow pre-authorization is created.
7. Record outcomes and verification in a durable task ledger.

The demo does not require Grok credentials because it illustrates orchestration and policy, not provider API syntax.

## How this maps to the xAI API

For an xAI API deployment:

- use Grok for reasoning/drafting/tool selection;
- map the generic tool capabilities to xAI-supported tools, custom functions, or remote MCP as appropriate;
- keep task state, schedules, secrets, approvals, and the audit ledger in the host application unless the selected runtime supplies them;
- resume from durable state rather than hidden model reasoning.

## Turning the demo into a real employee

Replace one layer at a time:

1. **Synthetic prospect input** → approved CRM/web-research connector.
2. **Deterministic draft template** → selected model/runtime.
3. **Simulated send** → scoped email connector or function.
4. **Local JSON ledger** → durable database/event log.
5. **CLI invocation** → scheduler, queue, webhook, or Grok Bot routine.
6. **CLI approval flag** → human approval UI or policy service.

Do not remove the authority gate just because a provider can technically execute the action.

## Example production flow

```text
Routine / queue event
  ↓
Load employee-contract.yaml
  ↓
Retrieve prospect from CRM
  ↓
Research current evidence
  ↓
Grok / GPT / Claude / Gemini / local model drafts outreach
  ↓
Authority matrix classifies external send as A3
  ↓
Human approves
  ↓
Email connector sends
  ↓
Read-back verifies provider message ID + recipient
  ↓
Durable ledger records outcome
```

That is the core idea of this repository: **model intelligence is replaceable; employee operations are durable.**
