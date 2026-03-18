# MCP Proxy (Loja-Teste)

Minimal FastAPI proxy that forwards `search_shop_catalog` requests to the Storefront MCP endpoint and returns a parsed JSON payload.

Setup

1. Create a virtual environment and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. Set the `STORE_DOMAIN` environment variable to your preview domain (the one shown by `shopify app dev`), for example:

Windows PowerShell:

```powershell
$env:STORE_DOMAIN = 'loja-teste-123456789123456953.myshopify.com'
uvicorn backend.app.main:app --reload --port 8000
```

Usage

Request example (curl):

```bash
curl -sS -X POST "http://localhost:8000/search" -H "Content-Type: application/json" -d '{"query":"snowboard","context":"cliente procura"}'
```

Notes

- This proxy is minimal and intended for development. Add rate-limiting, caching, auth, and sanitization before production use.
- The proxy expects the Storefront MCP to be reachable from your machine using the preview domain.
