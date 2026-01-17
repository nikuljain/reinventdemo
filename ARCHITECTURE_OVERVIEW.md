# Architecture Overview — Reinvent Demo

This folder contains a compact demo that shows three ways to expose Azure APIs as "tools" callable by a language model (Bedrock). Use the `usecase-1-direct` and `usecase-2-gateway` apps as starting points.

Diagrams (in `diagrams/`):

- `architecture.svg` — High-level system architecture showing Browser → App Server → Bedrock → (Gateway) → Azure APIs.
- `sequence.svg` — Sequence flow for a single request: POST /api/chat → Bedrock.converse → toolUse → toolResult → final output.
- `components.svg` — Component breakdown showing responsibilities of Browser, App Server, Bedrock, and Azure APIs.

Key points

- The app server provides an agentic loop: it calls `bedrock.converse()` and when the model returns `toolUse`, the server executes the HTTP call to the Azure API and returns `toolResult` back to the model until an `end_turn` is produced.
- Azure endpoints in this demo currently return HTML dashboards — the server returns them as text. We can add HTML parsing to return structured JSON fields (Traefik version, mTLS, headers, proxy IPs).
- Use Case 2 is configured to optionally route Bedrock calls via an AgentCore Gateway (MCP) — if `gateway_id.txt` contains a gateway id, the Bedrock client is constructed with an `endpoint_url` pointing to the gateway.

Next steps

- If you want structured output for the tech team, I can add parsers that extract specific fields from the HTML dashboards and present them as cards in the UI.
- I can also produce PNG/PDF versions of the SVG diagrams if you need them for slides.
