import os, requests
from dotenv import load_dotenv
load_dotenv()

token = os.environ["CF_API_TOKEN"]

resp = requests.get(
    "https://api.cloudflare.com/client/v4/user/tokens/verify",
    headers={"Authorization": f"Bearer {token}"},
)
print(resp.status_code, resp.json())