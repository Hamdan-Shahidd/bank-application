# test_image_gen.py
import os, base64, requests
from dotenv import load_dotenv
load_dotenv()

acct = os.environ["CF_ACCOUNT_ID"]
token = os.environ["CF_API_TOKEN"]

resp = requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell",
    headers={"Authorization": f"Bearer {token}"},
    json={"prompt": "a golden retriever wearing sunglasses, studio photo"},
    timeout=60,
)
print("status:", resp.status_code)
data = resp.json()
print("success:", data.get("success"))
if not data.get("success"):
    print("errors:", data.get("errors"))
else:
    with open("test_output.png", "wb") as f:
        f.write(base64.b64decode(data["result"]["image"]))
    print("wrote test_output.png")