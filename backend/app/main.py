from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import httpx

app = FastAPI(title="MCP Proxy - Loja-Teste")


class SearchRequest(BaseModel):
    query: str
    context: str = "user"


STORE_DOMAIN = os.getenv("STORE_DOMAIN", "loja-teste-123456789123456953.myshopify.com")
MCP_URL = f"https://{STORE_DOMAIN}/api/mcp"


@app.post("/search")
async def search(req: SearchRequest):
    body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": "t1",
        "params": {
            "name": "search_shop_catalog",
            "arguments": {"query": req.query, "context": req.context},
        },
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.post(MCP_URL, json=body, headers={"Content-Type": "application/json"})
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Request error: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"MCP returned {r.status_code}")

    data = r.json()

    # The Storefront MCP often embeds the useful payload in result.content[0].text as a JSON string
    if data.get("result") and data["result"].get("content"):
        text = data["result"]["content"][0].get("text")
        try:
            payload = json.loads(text)
        except Exception:
            payload = text
    else:
        payload = data

    return {"ok": True, "mcp": payload}
