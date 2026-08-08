import httpx

data = {"persona": {"name": "AURA", "domain": "AI Technology Research"}}
res = httpx.post("http://localhost:8000/api/agent/init", json=data)
print(res.json())
