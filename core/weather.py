"""
Weather fetching for a fixed set of cities, with a simple TTL cache.
Mirrors core/market.py's structure so both the REST endpoint and the
agent tool call the same cached function.
"""
import time
import requests
from logging_config import logger

# Hardcoded coordinates — Open-Meteo takes lat/lon, not city names.
CITIES = {
    "Lahore":    {"lat": 31.5497, "lon": 74.3436},
    "London":    {"lat": 51.5072, "lon": -0.1276},
    "New York":  {"lat": 40.7128, "lon": -74.0060},
    "Baltimore": {"lat": 39.2904, "lon": -76.6122},
    "Chicago":   {"lat": 41.8781, "lon": -87.6298},
}

# WMO weather codes -> readable label, covering the common cases.
# Full table: https://open-meteo.com/en/docs (see "WMO Weather interpretation codes")
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Freezing fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
}


def _describe(code):
    return WEATHER_CODES.get(code, f"Unknown (code {code})")


CACHE_TTL_SECONDS = 300   # weather changes slowly — 5 min is plenty fresh
_cache = {"data": None, "fetched_at": 0}


def _fetch_live():
    results = []
    errors = []
    for city, coords in CITIES.items():
        try:
            resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "current_weather": True,
                },
                timeout=10,
            )
            resp.raise_for_status()
            cw = resp.json()["current_weather"]
            results.append({
                "city": city,
                "temperature_c": cw["temperature"],
                "windspeed_kmh": cw["windspeed"],
                "condition": _describe(cw["weathercode"]),
                "observed_at": cw["time"],
            })
        except Exception as e:
            logger.warning(f"WEATHER FETCH FAILED | city={city} | {e}")
            errors.append(city)

    if not results:
        raise RuntimeError(f"All weather fetches failed: {errors}")
    if errors:
        logger.warning(f"WEATHER PARTIAL FAILURE | missing={errors}")
    return results


def get_weather(force_refresh = False , city = ""):
    """
    Returns cached weather if fresh (< CACHE_TTL_SECONDS old), else fetches.
    Single function called by both the REST route and the agent tool.
    """
    now = time.time()
    is_stale = (now - _cache["fetched_at"]) > CACHE_TTL_SECONDS

    if force_refresh or is_stale or _cache["data"] is None:
        try:
            _cache["data"] = _fetch_live()
            _cache["fetched_at"] = now
            logger.info(f"WEATHER REFRESHED | {len(_cache['data'])} cities")
        except Exception as e:
            logger.warning(f"WEATHER REFRESH FAILED, serving stale/empty | {e}")
            if _cache["data"] is None:
                return {"cities": [], "stale": False, "error": str(e)}
            return {"cities": _cache["data"], "stale": True, "error": str(e)}

    return {"cities": _filter(_cache["data"] , city), "stale": False, "error": None}


def _filter(cities, city):
    if not city:
        return cities
    matches = [c for c in cities if c["city"].lower() == city.strip().lower()]
    return matches if matches else cities  # fall back to all 5 if no match