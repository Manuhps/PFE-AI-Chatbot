import requests
import os
import json

url = os.getenv('PROXY_URL', 'http://localhost:8000/search')

payload = {
    "query": "snowboard",
    "context": "cliente procura"
}

resp = requests.post(url, json=payload)
try:
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception:
    print(resp.text)
