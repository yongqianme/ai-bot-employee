# Runtime Adapter

The employee contract is runtime-neutral. The demo CLI accepts `--runtime` to show how the same employee maps to different environments.

## Grok Bot

- Employee role → named Grok Bot.
- Repeatable procedure → Bot skill.
- Recurring/event-driven work → routine.
- Research/files/browser/SaaS → Grok Bot tools/connectors or approved MCP connector.
- A3 send → preserve an approval gate before any external message.
- Durable employee policy remains in the employee contract; do not rely on conversational context as the source of truth.

## xAI API

- Reasoning/drafting → Grok model through the host application's selected xAI API surface.
- Tools → xAI built-ins, custom function calling, or remote MCP as available.
- Durable task state, scheduler, secrets, approvals, and audit log → host application unless the chosen runtime explicitly supplies them.

## OpenAI / Anthropic / Gemini / Local

Map the same generic capabilities to the provider/runtime's instruction layer and tool/function interface. Keep authority, state, approvals, and audit behavior semantically equivalent.

## Demo limitation

`run_demo.py` does not call any model or external service. It simulates the orchestration contract so the approval and ledger behavior can be inspected without credentials or cost.
