# Research & Prototype Plan — Shopify AI Chatbot (React + Python)

Date: 2026-03-17

Goal
- Build an AI-powered chatbot prototype for Shopify stores (Xtreme) with a React frontend and Python backend that is grounded using Shopify MCP tools and the Admin/Storefront APIs.

Scope
- Minimal viable prototype that: answers product/store questions, performs cart operations (Storefront MCP), and can create/update products via the Admin API (developer demo). Integrations: MCP (dev), Admin GraphQL, Storefront MCP.

High-level architecture
- Frontend: React (Vite + TypeScript) chat UI component embedded in merchant/admin panel or a dev page.
- Backend: Python (FastAPI) serving as orchestration layer and secure token store; communicates with LLMs and Shopify Admin API (server-to-server).
- LLM layer: use hosted LLM (OpenAI / local LLM) or LLM orchestration (LangChain) — the MCP server will be used for development validation and schema grounding.
- Dev tools: Shopify Dev MCP server for schema introspection and validation while developing.

Core features (MVP)
- Conversational QA about store/catalog (use `search_shop_catalog`).
- Cart management actions via Storefront MCP (`get_cart`, `update_cart`).
- Admin ops demo: create product (validated GraphQL mutation) via Admin GraphQL (with example script already added).
- Grounding/validation: use MCP tools (`learn_shopify_api`, `introspect_graphql_schema`, `validate_graphql_codeblocks`, `validate_theme` when needed).

Data & security
- Store secrets (Admin API token) in environment variables or a secrets store; never send tokens to the client.
- For Customer Accounts or PII, follow OAuth PKCE and Level 2 procedures; do not request PII until approved.

Developer workflow (how MCP fits in)
- Local dev: run `npx -y @shopify/dev-mcp@latest` (done).
- Use Copilot Chat / Dev MCP tools when crafting GraphQL and Liquid changes: call `learn_shopify_api`, then `introspect_graphql_schema`, then `validate_graphql_codeblocks`.
- Use `validate_theme` for theme work and `validate_component_codeblocks` for Polaris components.

Implementation tasks (ordered)
1. Bootstrap repo
   - Frontend: `npm create vite@latest frontend --template react-ts`
   - Backend: `python -m venv .venv && pip install fastapi uvicorn httpx pydantic` (create `backend/`)
2. Chat UI
   - Minimal chat widget with messages, input, and action buttons (add to `frontend/src/ChatWidget.tsx`).
3. Backend endpoints
   - `/api/chat` — accepts user message and session metadata, returns assistant reply.
   - `/api/action/cart` — backend wrapper to call Storefront MCP or Storefront API.
4. LLM orchestration
   - Implement a small chain: intent classification → tool selection (call Storefront or Admin) → grounding via MCP (during development) → call API → format reply.
5. Admin mutation example
   - Use `scripts/create_product_example.js` to show product creation; integrate that example into backend as a controlled operation (with proper auth checks).
6. Testing and validation
   - For each GraphQL operation, use MCP `validate_graphql_codeblocks` in the dev loop.
   - Unit tests for backend endpoints (pytest) and E2E for chat UI (Playwright).

Milestones & timeline (suggested)
- Week 1: Repo scaffold, MCP validation flow, example script wired to backend (fast test harness).
- Week 2: Chat UI + backend `/api/chat`, simple LLM orchestration, cart actions via Storefront MCP.
- Week 3: Admin mutation flows (create product), tests, basic QA and demo.

Validation & success criteria
- The assistant can produce GraphQL mutations validated by MCP tools automatically.
- Chat UI demonstrates a cart add flow that returns a `checkout_url`.
- Able to create a product via the demo endpoint using a valid Admin token (in a dev store).

Deliverables
- `frontend/` React app with chat widget.
- `backend/` FastAPI app with `/api/chat` and action endpoints.
- `scripts/create_product_example.js` (already added).
- Documentation: `PROPOSAL_CHATBOT_PLAN.md`, updated `CHANGES_MCP_SETUP.md`, run instructions.

Risks & mitigations
- PII and permissions: require a dev store and avoid PII flows until OAuth/Level2 approved.
- Rate limits: implement retries & backoff.

Commands (quick start)
```powershell
# Start Dev MCP (you already did):
npx -y @shopify/dev-mcp@latest

# Backend (from repo root)
cd backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Next steps (I can take now)
- Generate the initial `frontend/` and `backend/` scaffolding and a minimal `main.py` + `ChatWidget.tsx` scaffold.
- Or, produce a more detailed task breakdown and issue list for sprint 1.
