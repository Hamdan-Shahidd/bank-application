"""
Caching and rate limiting aare essential because limited 1000 calls per month in the free tier.
The main goals of this class are;
1. Search the web using tavily.
2. Avoid wasting API credits by caching the results.
3. Stop user from making too many requests at once.
4. Handle API errors.
5. Return the result in the form of python dictionary instead of raw Tavily data. 
"""
import os
import time
import hashlib
import requests # send HTTP requests to tavily
from logging_config import logger

# Tavily configurations. The API endpoint is https://api.tavily.com/search
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_URL = "https://api.tavily.com/search"

# Search Limits
MAX_QUERY_LENGTH = 300
DEFAULT_MAX_RESULTS = 4

# Query-keyed cache with TTL for 15 minutes. 
CACHE_TTL_SECONDS = 900
MAX_CACHE_ENTRIES = 50
_cache = {}          # key -> {"data": ..., "fetched_at": ...}
_cache_order = []    # insertion order, for bounded eviction

# Per-user rate limit. 1,000 credits/month is ~33/day total across ALL
# users, so this is deliberately tight. Per user rate limiting.
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW_SECONDS = 3600
_search_log = {}     # user_id -> [timestamps]

#  Creating a cache key. It becomes something like "general : python tutorials". The sah256 becomes the cache key.
def _cache_key(query, topic):
    return hashlib.sha256(f"{topic}:{query.strip().lower()}".encode()).hexdigest()

# Getting something from the cache. Check if their is an entry for a specified question. If yes then
# finds the time that entry was cached. If it is between 15 minutes then returns that. 
def _cache_get(key):
    entry = _cache.get(key)
    if not entry:
        return None
    if time.time() - entry["fetched_at"] > CACHE_TTL_SECONDS:
        return None          # expired; leave it, it'll be overwritten
    return entry["data"]

# Getting the data into the cache. THe data is stored along with the timestmap.
# Once their are 50 entries, the oldest one will be removed from the cache.
def _cache_put(key, data):
    _cache[key] = {"data": data, "fetched_at": time.time()}
    _cache_order.append(key)
    while len(_cache_order) > MAX_CACHE_ENTRIES:
        oldest = _cache_order.pop(0)
        _cache.pop(oldest, None)

# Check the rate limiting for the user. Check the dictionary for the last hour.
def _rate_limited(user_id):
    now = time.time()
    stamps = [
        t for t in _search_log.get(user_id, [])
        if now - t < RATE_LIMIT_WINDOW_SECONDS
    ]
    _search_log[user_id] = stamps
    return len(stamps) >= RATE_LIMIT_MAX

# Recording a successful search in the dictionary of the user along with the timestamps. 
def _record_search(user_id):
    _search_log.setdefault(user_id, []).append(time.time())

# Main: Topic can be one of general, finance, news.
def web_search(user_id, query, topic="general"):
    # Checks if the Tavily is configured.
    if not TAVILY_API_KEY:
        return {
            "answer": None, "results": [], "query": query,
            "cached": False, "error": "Web search is not configured on the server."
        }

    # Validates the query and removes the whitespace.
    query = (query or "").strip()
    # If the query is empty in other words if the query is ""
    if not query:
        return {
            "answer": None, "results": [], "query": query,
            "cached": False, "error": "Please provide something to search for."
        }

    # Validates the length of the query.
    if len(query) > MAX_QUERY_LENGTH:
        query = query[:MAX_QUERY_LENGTH]
        logger.info(f"SEARCH QUERY TRUNCATED | to {MAX_QUERY_LENGTH} chars")

    # Validates the topic of the query. The default one is general.
    if topic not in ("general", "news", "finance"):
        topic = "general"

    # Cache check BEFORE the rate limit a cache hit costs no credit,
    # so it shouldn't count against the user's quota.
    key = _cache_key(query, topic)
    hit = _cache_get(key)
    # If the result exists, immediately returns it.
    if hit is not None:
        logger.info(f"SEARCH CACHE HIT | query={query[:60]!r}")
        return {**hit, "cached": True, "error": None}

    # Rate limiting: Check wether the user has done 10 searches. If yes then gives a warning in looging.
    if _rate_limited(user_id):
        logger.warning(f"SEARCH RATE LIMITED | user_id={user_id}")
        return {
            "answer": None, "results": [], "query": query, "cached": False,
            "error": f"Search limit reached ({RATE_LIMIT_MAX} per hour). Try again later."
        }
    # Calling Tavily
    try:
        # This is the actual API request. 
        resp = requests.post(
            TAVILY_URL,
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            json={
                "query": query,
                "search_depth": "basic",     # explicit: takes 1 credit. I fadvanced search is done that takes 2 credits. 
                "auto_parameters": False,    # explicit: don't let it upgrade to advanced
                "max_results": DEFAULT_MAX_RESULTS,
                "topic": topic,
                "include_answer": True,      # Tavily synthesizes; see 1.3
                "include_raw_content": False,
                "include_images": False,
            },
            timeout=30,
        )
        resp.raise_for_status() # Checks wether the tavily returned an HTTP error.
        data = resp.json()

        # Parse tavily response. Instead if returning everything the tavily returns, it only returns the following fields.
        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": (r.get("content", "") or "")[:400],
                "score": round(float(r.get("score", 0)), 3),
            }
            for r in data.get("results", [])
        ]

        # Our own standard response. This is displayed on the frontend. 
        # The frontend don;t have to know the whole travily responsee. 
        payload = {
            "answer": data.get("answer"),
            "results": results,
            "query": query,
        }

        # Cache the useful result
        _cache_put(key, payload)
        # Recird the user used the search with a timestamp
        _record_search(user_id)
        logger.info(f"SEARCH PERFORMED | user_id={user_id} | topic={topic} "
                    f"| query={query[:60]!r} | results={len(results)}")
        return {**payload, "cached": False, "error": None}

    except requests.Timeout:
        logger.warning(f"SEARCH TIMEOUT | query={query[:60]!r}")
        return {
            "answer": None, "results": [], "query": query, "cached": False,
            "error": "The search timed out. Please try again."
        }
    
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        logger.warning(f"SEARCH HTTP ERROR | status={status} | {e}")

        if status == 401:
            return {
                "answer": None, "results": [], "query": query, "cached": False,
                "error": "Search service credentials were rejected."
            }
        
        if status == 429:
            return {
                "answer": None, "results": [], "query": query, "cached": False,
                "error": "Search quota exhausted. Try again later."
            }
        
        return {
            "answer": None, "results": [], "query": query, "cached": False,
            "error": "The search service returned an error."
        }
    
    except Exception as e:
        logger.warning(f"SEARCH FAILED | {e}")
        return {
            "answer": None, "results": [], "query": query, "cached": False,
            "error": "Could not complete the search right now."
        }

"""
GENERAL QUESTIONS: 
Q: Where is the data stored in the cache? 
A: The data is stored in the cache in the simple python dictionary. 
   So the data is stored in the RAM of the server running this python program.
   It's an in-memory application level cache with TTL. 
   Their is a single _cache shared by all users of that python process.

Q: What does ** means before hit or any other?
A: ** is a dixtionary unpacking operator. It takes all key value pairs inside hit and
   places them into the new dictionary. 
"""