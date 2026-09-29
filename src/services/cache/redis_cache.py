"""
Week 6 — Redis response cache.

Exact-match caching: the same query + same parameters produce the same
cache key, so a repeat call skips the whole retrieve+generate pipeline
(~15-20s) and returns in ~100ms. This is *not* semantic caching (a
rephrased question is still a miss) — that's a stretch goal, not this
week's job.
"""

import hashlib
import json

import redis


class RedisCache:
    def __init__(self, host: str, port: int, ttl_hours: int) -> None:
        self.ttl_seconds = ttl_hours * 3600
        # TODO: self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.client: redis.Redis | None = None  # TODO

    def _build_key(self, query: str, **params) -> str:
        """Build a stable cache key from the query + any extra parameters.

        TODO: hash (query, sorted(params.items())) with hashlib.sha256
        into something like f"rag:ask:{digest.hexdigest()}" — stable
        regardless of dict ordering, and short enough to be a sane key.
        """
        raise NotImplementedError

    def get(self, query: str, **params) -> dict | None:
        """TODO:
        key = self._build_key(query, **params)
        raw = self.client.get(key)
        return json.loads(raw) if raw else None

        Catch redis connection errors and return None — a Redis outage
        should degrade to "always miss", not crash requests.
        """
        raise NotImplementedError

    def set(self, query: str, value: dict, **params) -> None:
        """TODO:
        self.client.setex(self._build_key(query, **params), self.ttl_seconds, json.dumps(value))
        """
        raise NotImplementedError
