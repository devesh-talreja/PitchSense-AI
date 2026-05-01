"""
data_bridge.py
──────────────
Two-layer cache: disk (JSON file) + in-memory hot cache.

Layer 1 — Disk: JSON written to .pitchsense_cache.json
  • Survives server restarts, browser opens, Streamlit reruns.
  • TTL = 90 seconds per key.

Layer 2 — Memory: module-level dict, microsecond reads.
  • Falls back to disk if memory is cold (e.g., first hit after restart).

CricAPI Free Tier Protection:
  • currentMatches is only fetched when the disk cache is expired.
  • match_scorecard (premium endpoint) is gated by a _404_cache:
    If it returns 404/empty, we skip it for 10 minutes and serve
    the data from the /currentMatches payload instead.
  • Net result: at most 1 API call per 90 seconds regardless of
    how many browser sessions, reruns, or refreshes happen.
"""

import time
import json
import os
import logging

from config import MOCK_MODE, CACHE_TTL
import mock_data
import cricket_api

log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────
DISK_CACHE_PATH = os.path.join(os.path.dirname(__file__), ".pitchsense_cache.json")
SCORECARD_404_BACKOFF = 600   # 10 minutes before retrying a 404 scorecard
HOT_CACHE_TTL = CACHE_TTL     # in-memory hot cache TTL (seconds)

# ── Module-level state ────────────────────────────────────────────────
_hot:         dict[str, tuple[float, object]] = {}   # key → (timestamp, data)
_match_store: dict[str, dict] = {}                   # match_id → normalized dict
_404_cache:   dict[str, float] = {}                  # match_id → last 404 timestamp


# ══════════════════════════════════════════════════════════════════════
# Layer 1: Disk Cache helpers
# ══════════════════════════════════════════════════════════════════════

def _disk_read() -> dict:
    """Read the full disk cache dict. Returns {} on any failure."""
    try:
        if os.path.exists(DISK_CACHE_PATH):
            with open(DISK_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        log.warning("Disk cache read error: %s", exc)
    return {}


def _disk_write(store: dict) -> None:
    """Persist the full cache dict to disk. Silent on failure."""
    try:
        with open(DISK_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f)
    except Exception as exc:
        log.warning("Disk cache write error: %s", exc)


def _disk_get(key: str, ttl: float = HOT_CACHE_TTL):
    """
    Return value from disk cache if it exists and is within TTL.
    Also populates the hot cache on hit.
    """
    store = _disk_read()
    entry = store.get(key)
    if entry:
        ts, val = entry["ts"], entry["val"]
        if time.time() - ts < ttl:
            # Also warm the hot cache
            _hot[key] = (ts, val)
            return val
    return None


def _disk_set(key: str, val) -> None:
    """Write a single key to disk cache (merges with existing data)."""
    store = _disk_read()
    store[key] = {"ts": time.time(), "val": val}
    _disk_write(store)


# ══════════════════════════════════════════════════════════════════════
# Layer 2: Hot (in-memory) Cache helpers
# ══════════════════════════════════════════════════════════════════════

def _hot_get(key: str, ttl: float = HOT_CACHE_TTL):
    entry = _hot.get(key)
    if entry:
        ts, val = entry
        if time.time() - ts < ttl:
            return val
    return None


def _hot_set(key: str, val) -> None:
    _hot[key] = (time.time(), val)


def _get(key: str, ttl: float = HOT_CACHE_TTL):
    """Check hot cache first, then disk cache."""
    v = _hot_get(key, ttl)
    if v is not None:
        return v
    return _disk_get(key, ttl)


def _set(key: str, val) -> None:
    """Write to both hot cache and disk simultaneously."""
    _hot_set(key, val)
    _disk_set(key, val)


# ══════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════

async def get_live_matches() -> list[dict]:
    """
    Returns normalized list of current matches.
    At most 1 real API call per 90 seconds regardless of how many
    sessions/reruns happen.
    """
    cached = _get("live_matches")
    if cached is not None:
        log.debug("Cache HIT — live_matches")
        return cached

    log.info("Cache MISS — fetching live matches from CricAPI")
    if MOCK_MODE:
        result = mock_data.get_mock_matches()
    else:
        result = await cricket_api.fetch_live_matches()
        if not result:
            log.warning("Live API returned empty — falling back to mock.")
            result = mock_data.get_mock_matches()

    # Index by match_id for O(1) scorecard lookups
    for m in result:
        mid = m.get("match_id")
        if mid:
            _match_store[mid] = m

    _set("live_matches", result)
    return result


async def get_scorecard(match_id: str) -> dict | None:
    """
    Returns the best scorecard we can get for a match.

    Priority order:
      1. Hot / disk cache (0 API calls)
      2. Data already in _match_store from /currentMatches (0 extra API calls)
      3. Dedicated /match_scorecard endpoint — ONLY if:
         a. The match has innings data not available from /currentMatches
         b. This match_id hasn't 404'd in the last 10 minutes
    """
    key = f"sc_{match_id}"
    cached = _get(key)
    if cached is not None:
        log.debug("Cache HIT — scorecard %s", match_id)
        return cached

    # Mock mode
    if MOCK_MODE or match_id.startswith("mock_"):
        result = mock_data.get_mock_scorecard(match_id)
        _set(key, result)
        return result

    # ── Try to serve from what /currentMatches already gave us ──────
    result = _match_store.get(match_id)

    # ── If innings data is missing, attempt dedicated endpoint ───────
    innings_missing = not result or (
        not result.get("innings1") and not result.get("innings2")
    )
    if innings_missing:
        now = time.time()
        last_404_ts = _404_cache.get(match_id, 0)
        if now - last_404_ts > SCORECARD_404_BACKOFF:
            log.info("Attempting scorecard endpoint for %s", match_id)
            detailed = await cricket_api.fetch_scorecard(match_id)
            if detailed and (detailed.get("innings1") or detailed.get("innings2")):
                result = detailed
                log.info("Scorecard endpoint returned data for %s", match_id)
            else:
                # Record 404 so we don't retry for SCORECARD_404_BACKOFF seconds
                _404_cache[match_id] = now
                log.warning(
                    "Scorecard 404 for %s — suppressing retries for %ds",
                    match_id, SCORECARD_404_BACKOFF
                )
        else:
            remaining = int(SCORECARD_404_BACKOFF - (now - last_404_ts))
            log.debug("Scorecard 404 backoff active for %s (%ds left)", match_id, remaining)

    # ── Final fallback: re-fetch /currentMatches and try again ───────
    if not result:
        log.info("No data in store for %s — re-fetching live list", match_id)
        await get_live_matches()
        result = _match_store.get(match_id)

    if result:
        _set(key, result)
    else:
        log.warning("Absolutely no data for %s — using mock fallback", match_id)
        result = mock_data.get_mock_scorecard("mock_mi_rcb_20260412")

    return result


async def get_last_5_overs(match_id: str) -> list:
    key = f"last5_{match_id}"
    cached = _get(key)
    if cached is not None:
        return cached

    sc = await get_scorecard(match_id)
    result = sc.get("last_5_overs", []) if sc else []
    _set(key, result)
    return result


def get_primary_match_id() -> str | None:
    if _match_store:
        return next(iter(_match_store))
    return None


def clear_cache():
    """Hard reset — clears all layers."""
    _hot.clear()
    _match_store.clear()
    # Also wipe disk cache
    try:
        if os.path.exists(DISK_CACHE_PATH):
            os.remove(DISK_CACHE_PATH)
    except Exception:
        pass
    log.info("All cache layers cleared")
