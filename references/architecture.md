# Model-agnostic AI employee architecture

Use this reference when the role needs persistent operation, multiple tools, or multiple models.

## Control plane vs intelligence plane

Keep durable policy outside the model.

**Control plane**
- employee contract;
- authority matrix;
- credentials and secrets;
- tool registry;
- scheduler/event triggers;
- durable task state;
- approval queue;
- audit ledger;
- cost/time budgets;
- model routing policy;
- evaluation suite.

**Intelligence plane**
- one or more LLMs;
- task planning/reasoning;
- summarization and drafting;
- tool selection;
- review/critique.

A model should be replaceable without rewriting the control plane.

## Minimal runtime loop

```text
trigger/request
    ↓
load employee contract + open task state
    ↓
retrieve minimal context
    ↓
plan next bounded step
    ↓
check authority / approval gate
    ↓
execute tool or create artifact
    ↓
verify observed result
    ↓
write task state + audit ledger
    ↓
complete / wait / escalate / schedule next trigger
```

## Recommended components

### 1. Event source
Examples: user message, cron schedule, webhook, queue event, incoming email, database change.

### 2. Work queue
Use durable IDs and explicit states such as `queued`, `running`, `waiting_approval`, `waiting_dependency`, `completed`, `failed`, `cancelled`.

### 3. State store
Persist artifacts, task status, next action, external IDs, deadlines, and verification results. Do not persist hidden chain-of-thought.

### 4. Tool gateway
Expose the smallest possible set of structured tools. Use scoped credentials. Prefer explicit schemas over free-form shell/browser control for high-impact systems.

### 5. Approval service
The model may propose an action; policy decides whether it can execute. Approval records should bind to a concrete action, target, and limit.

### 6. Model router
Use only when valuable. Possible routing fields:
- privacy class;
- required modality;
- context size;
- latency target;
- cost ceiling;
- tool support;
- domain specialization;
- independent-review requirement.

### 7. Verification layer
After side effects, query the system of record or inspect the artifact. Tool invocation success is not equivalent to business outcome success.

### 8. Ledger and observability
Capture request, plan summary, evidence refs, tools, approvals, state changes, verification, errors, and usage/cost.

## Multi-agent pattern

Prefer a single employee until role boundaries justify multiple agents.

When multiple agents are justified, use one of these patterns:

- **Manager + specialists:** manager retains responsibility and calls specialists as tools.
- **Handoff:** ownership transfers to a specialist with an explicit task and context package.
- **Independent review:** two or more models solve/review independently against criteria; an adjudicator compares evidence.
- **Pipeline:** deterministic stage ownership for research → analysis → draft → verification.

Avoid uncontrolled peer chat. Every delegation needs an owner, expected output, budget, and stop condition.
