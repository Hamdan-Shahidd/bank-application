"""
Text-to-image via Cloudflare Workers AI (FLUX-1-schnell).
Free tier: 10,000 neurons/day (~223 images), no credit card.
"""
import os
import base64
import hashlib
import requests
from logging_config import logger

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")

MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"

MAX_PROMPT_LENGTH = 500

# Prompt-keyed cache. Bounded by COUNT, not time — a base64 512x512 PNG is
# roughly 400-700KB as a string, so 20 entries is ~10MB of memory. Do not
# raise this carelessly.
_cache = {}
_cache_order = []
MAX_CACHE_ENTRIES = 20

# Per-user rate limit. 223 images/day is the account-wide budget.
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW_SECONDS = 3600
_gen_log = {}


def _cache_key(prompt):
    return hashlib.sha256(prompt.strip().lower().encode()).hexdigest()


def _cache_put(key, value):
    _cache[key] = value
    _cache_order.append(key)
    while len(_cache_order) > MAX_CACHE_ENTRIES:
        _cache.pop(_cache_order.pop(0), None)


def _rate_limited(user_id):
    import time
    now = time.time()
    stamps = [t for t in _gen_log.get(user_id, [])
              if now - t < RATE_LIMIT_WINDOW_SECONDS]
    _gen_log[user_id] = stamps
    return len(stamps) >= RATE_LIMIT_MAX


def _record_gen(user_id):
    import time
    _gen_log.setdefault(user_id, []).append(time.time())


def generate_image(user_id, prompt):
    """
    Returns {"image_b64": str|None, "prompt": str, "cached": bool, "error": str|None}
    image_b64 is a base64 PNG, ready to embed as a data URI.
    """
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return {"image_b64": None, "prompt": prompt, "cached": False,
                "error": "Image generation is not configured on the server."}

    prompt = (prompt or "").strip()
    if not prompt:
        return {"image_b64": None, "prompt": prompt, "cached": False,
                "error": "Please describe what you'd like to see."}

    if len(prompt) > MAX_PROMPT_LENGTH:
        prompt = prompt[:MAX_PROMPT_LENGTH]
        logger.info(f"IMAGE PROMPT TRUNCATED | to {MAX_PROMPT_LENGTH} chars")

    # Cache check BEFORE rate limit — a cache hit costs no neurons, so it
    # shouldn't count against the user's quota.
    key = _cache_key(prompt)
    if key in _cache:
        logger.info(f"IMAGE CACHE HIT | prompt={prompt[:60]!r}")
        return {"image_b64": _cache[key], "prompt": prompt,
                "cached": True, "error": None}

    if _rate_limited(user_id):
        logger.warning(f"IMAGE RATE LIMITED | user_id={user_id}")
        return {"image_b64": None, "prompt": prompt, "cached": False,
                "error": f"Generation limit reached ({RATE_LIMIT_MAX} per hour)."}

    try:
        resp = requests.post(
            CF_URL,
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json={"prompt": prompt},
            timeout=60,   # generation takes seconds; a 10s timeout would fail
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success", False):
            logger.warning(f"IMAGE GEN API ERROR | {data.get('errors')}")
            return {"image_b64": None, "prompt": prompt, "cached": False,
                    "error": "The image service rejected that request."}

        # FLUX returns base64 in result.image.
        # SDXL would instead return RAW PNG BYTES — you'd use
        # base64.b64encode(resp.content).decode() and skip .json() entirely.
        image_b64 = data["result"]["image"]

        _cache_put(key, image_b64)
        _record_gen(user_id)
        logger.info(f"IMAGE GENERATED | user_id={user_id} | prompt={prompt[:60]!r}")
        return {"image_b64": image_b64, "prompt": prompt,
                "cached": False, "error": None}

    except requests.Timeout:
        logger.warning(f"IMAGE GEN TIMEOUT | prompt={prompt[:60]!r}")
        return {"image_b64": None, "prompt": prompt, "cached": False,
                "error": "Image generation timed out. Please try again."}
    except Exception as e:
        logger.warning(f"IMAGE GEN FAILED | {e}")
        return {"image_b64": None, "prompt": prompt, "cached": False,
                "error": "Could not generate the image right now."}