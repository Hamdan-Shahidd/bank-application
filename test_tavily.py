# test_tavily.py
import os, requests, json
from dotenv import load_dotenv
load_dotenv()

resp = requests.post(
    "https://api.tavily.com/search",
    headers={"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}"},
    json={
        "query": "current inflation rate in Pakistan",
        "search_depth": "basic",
        "max_results": 4,
        "include_answer": True,
    },
    timeout=30,
)
print("status:", resp.status_code)
data = resp.json()
print("\nANSWER:", data.get("answer"))
print("\nSOURCES:")
for r in data.get("results", []):
    print(f"  [{r['score']:.2f}] {r['title']}\n        {r['url']}")