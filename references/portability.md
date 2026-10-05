# Portability across AI models and runtimes

"Works with all AI models" must be interpreted correctly: the durable employee contract can be model-agnostic, but autonomous behavior depends on the surrounding runtime.

## Portability layers

### Layer 1 — Instruction portability
Any model that can follow structured natural-language instructions can use the employee contract. If the host supports Agent Skills, package the workflow in `SKILL.md`. Otherwise use the portable prompt fallback.

### Layer 2 — Tool portability
Represent tools as generic capabilities first:

```text
capability: send_message
input: recipient, subject?, body, attachments?
side_effect: external communication
verification: returned message ID + optional read-back
```

Then map the capability to the host's native function/tool interface or to an MCP server.

MCP is a useful tool interoperability layer, but it is not mandatory. A native tool with equivalent semantics is acceptable.

### Layer 3 — State portability
Persist state in a runtime-controlled store using provider-neutral data structures. Do not assume the model provider stores long-term task state.

Minimum resumable task state:
- task ID;
- goal;
- current status;
- completed steps;
- artifacts/external IDs;
- unresolved dependencies;
- pending approval;
- next action;
- deadline;
- verification status.

### Layer 4 — Schedule/event portability
Use the host's scheduler, cron, job queue, webhook, or automation system. The model does not create persistence merely by being told to "keep monitoring."

### Layer 5 — Agent-to-agent portability
If independently hosted agents from different vendors must discover and collaborate with each other, an A2A-compatible interface can provide a neutral protocol. Keep A2A optional for simple single-runtime designs.

## Runtime adapter contract

For each deployment document:

```yaml
runtime:
  name: <host/runtime>
  instruction_surface: <system|developer|agents-md|skill|other>
  skills_supported: true|false
  tool_interface: <native-functions|mcp|browser|computer|shell|other>
  state_store: <database/files/session-store/other>
  scheduler: <cron/automation/queue/webhook/none>
  approvals: <human-review/policy-engine/manual/none>
  secrets: <credential-store>
  observability: <logs/traces/ledger>
  agent_interop: <a2a|native-handoffs|none>
```

## Provider examples

Keep these examples conceptual; exact product APIs evolve.

### OpenAI-style runtime
- load the skill or instruction core;
- expose native tools and/or MCP;
- store durable task state outside ephemeral model context;
- use human review for material side effects;
- re-run evaluations when changing model or reasoning configuration.

### Anthropic-style runtime
- install/load the Agent Skill;
- expose tools/MCP through the host;
- isolate code/browser access;
- persist task state and approvals outside the conversational transcript when durable operation is required.

### Gemini-style runtime
- mount skill/agent instruction files when supported;
- map tools through function calling, native tools, or MCP;
- keep scheduling/state/approval in the runtime rather than in prompt text.

### Local/open-model runtime
- inject the instruction core in the strongest supported instruction channel;
- use a local orchestrator for tool calls, state, scheduling, and permissions;
- validate tool-call arguments because smaller/local models may be less reliable at structured invocation;
- prefer local tools/data for privacy when that is the deployment goal.

## Capability degradation table

| Missing runtime capability | Required behavior |
|---|---|
| No tools | Draft/plan only; never claim execution |
| No durable state | Interactive employee only; no unattended multi-run work |
| No scheduler/events | User-triggered only |
| No approval mechanism | Disable material side effects or require synchronous user confirmation |
| No secure credential store | Do not give the model raw long-lived secrets |
| No tracing/logging | Restrict autonomy; keep an application-level ledger |
| No A2A | Use native handoffs/tools or a single orchestrator |

## Model-swap test

A build is portable only if a new model can continue a paused task from:
1. employee contract;
2. current task state;
3. referenced artifacts/data;
4. approval records;
5. task ledger;
without access to the previous model's hidden reasoning.
