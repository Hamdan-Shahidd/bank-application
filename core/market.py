"""
Crypto price fetching with a simple TTL cache.
Kept separate from api/ and ai/ so both the REST endpoint and the agent
tool call the same cached function instead of duplicating fetch logic.
"""
import time
import yfinance as yf
from logging_config import logger

# Ticker -> display symbol. Yahoo's crypto format is "<COIN>-<FIAT>".
COINS = {
    "BTC-USD": "BTC",
    "ETH-USD": "ETH",
    "SOL-USD": "SOL",
    "ADA-USD": "ADA",
    "DOGE-USD": "DOGE",
}
# The fetched prices will be considered fresh for 30 seconds.
CACHE_TTL_SECONDS = 30
# The following is the in-memory cache
_cache = {"data": None, "fetched_at": 0}

"""
This is the function that talks to the yfinance. The _ in the start of the function means that this is private/helper function.
It has two lists, prices and errors. 
"""
def _fetch_live():
    """Hits yfinance for each ticker. Raises on total failure."""
    prices = []
    errors = []
    # Loop through every coin.
    for ticker, symbol in COINS.items():
        try:
            # Fetch price history. History is actually a pandas dataframe.
            hist = yf.Ticker(ticker).history(period="1d", interval="5m")
            if hist.empty:
                errors.append(symbol)
                continue
            last_close = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[0])
            change_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close else 0.0
            # Builds the result: Create a clean dictionary for each coin.
            prices.append({
                "symbol": symbol,
                "ticker": ticker,
                "price_usd": round(last_close, 2),
                "change_pct_today": round(change_pct, 2),
            })
        except Exception as e:
            logger.warning(f"CRYPTO FETCH FAILED | ticker={ticker} | {e}")
            errors.append(symbol)

    if not prices:
        raise RuntimeError(f"All crypto fetches failed: {errors}")
    if errors:
        logger.warning(f"CRYPTO PARTIAL FAILURE | missing={errors}")
    return prices

"""
This is the main function that our FAST API and agent calls. 
"""
def get_crypto_prices(force_refresh=False , symbol=""):
    """
    Returns cached prices if fresh (< CACHE_TTL_SECONDS old), else fetches.
    This is the single function both the REST route and the agent tool call.
    """
    now = time.time()
    # Determine wether the cache is stale or not.
    is_stale = (now - _cache["fetched_at"]) > CACHE_TTL_SECONDS

    # Conditions to fetch data: 
    if force_refresh or is_stale or _cache["data"] is None:
        try:
            _cache["data"] = _fetch_live()
            _cache["fetched_at"] = now
            logger.info(f"CRYPTO PRICES REFRESHED | {len(_cache['data'])} coins")
        except Exception as e:
            logger.warning(f"CRYPTO REFRESH FAILED, serving stale/empty | {e}")
            if _cache["data"] is None:
                # Never successfully fetched, nothing to fall back to
                return {"prices": [], "stale": False, "error": str(e)}
            # Serve the last good data rather than failing the whole request
            return {"prices": _cache["data"], "stale": True, "error": str(e)}

    return {"prices": _filter(_cache["data"] , symbol), "stale": False, "error": None}


def _filter(prices, symbol):
    if not symbol:
        return prices
    matches = [p for p in prices if p["symbol"].lower() == symbol.strip().lower()]
    return matches if matches else prices