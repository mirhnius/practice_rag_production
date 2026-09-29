# Week 6 — Production Monitoring & Caching

## What you're building this week

Two things that don't change what the RAG pipeline *answers*, only how
well it survives being used for real: a cache so repeated questions
don't re-run the full 15-20 second pipeline, and tracing so you can see
what actually happened inside a request after the fact.

## Concepts you need before writing code

### Exact-match caching, and why it's *exact*

The cache key is built from the query text plus every parameter that
affects the answer (`top_k`, `use_hybrid`, model, ...) — same inputs,
same cache key, same cached response. "What are transformers?" and
"what are transformers" (different case) would, with a naive key,
*not* match — whether you normalize case/whitespace before hashing is a
design choice, not a requirement. What this is **not**: semantic
caching, where a *rephrased* question ("explain transformers" vs. "what
are transformers?") would hit the same cache entry. That needs
comparing query embeddings for similarity, which is real extra
complexity — the course explicitly leaves it as a future upgrade, and so
does this scaffold.

### Building a stable cache key

You can't use the raw query string as a Redis key directly (special
characters, length limits, and it wouldn't include the extra
parameters). Hash `(query, sorted(params.items()))` — sorting the
params first matters, because `{"top_k": 3, "use_hybrid": True}` and
`{"use_hybrid": True, "top_k": 3}` are the same request but would hash
differently as unsorted dicts.

### TTL: why cached answers expire

New papers get ingested over time (Week 2's pipeline could run daily).
A cached answer from last week might be missing a paper published
yesterday. A TTL (this course uses 24 hours) bounds how stale a cached
answer can get, trading a little cache-hit rate for correctness.

### Cache outages shouldn't become request failures

If Redis is down, `RedisCache.get()` should return `None` (a "miss"),
not raise — the pipeline falls back to doing the full retrieve+generate
work, which is slower but still correct. A cache is an optimization; it
should never be a single point of failure for the whole app.

### Why tracing, separately from logging

`print()`/logs tell you *that* something happened; a trace tells you the
whole *shape* of one request — how long retrieval took vs. generation,
whether it was a cache hit, what the actual prompt and answer were —
all grouped together and viewable per-request in the Langfuse dashboard.
That's what makes "why was this one answer wrong" or "why did this one
request take 40 seconds" answerable without re-reading scattered log
lines.

## Files to implement, in order

1. **`src/config.py`** — add `redis_host`, `redis_port`, `redis_ttl_hours`,
   `langfuse_enabled`, `langfuse_public_key`, `langfuse_secret_key`,
   `langfuse_host`.
2. **`src/services/cache/redis_cache.py`** — `_build_key`, `get`, `set`.
3. **`src/services/langfuse_tracer.py`** — `trace_rag_call`.
4. **`src/routers/ask.py`** — wrap the existing `/api/v1/ask` handler:
   check the cache first, and if it's a miss, time the real pipeline,
   cache the result, and send a trace either way. (See the Week 6 TODO
   already sitting at the bottom of `ask()`'s docstring.)

## Walking through `scripts/week6_test_cache_and_tracing.py`

1. A quick round-trip test directly against `RedisCache` (`set` then
   `get`) — confirms the cache itself works before involving the whole
   HTTP pipeline.
2. Sends the *same* request to your running `/api/v1/ask` twice, timing
   both. If caching is wired in correctly, the second call should be
   dramatically faster than the first.
3. Reminds you to check the Langfuse dashboard for traces of both calls,
   if `LANGFUSE_ENABLED=true`.

## Success criteria

- [ ] `RedisCache.set(...)` then `.get(...)` round-trips the same value
- [ ] The second identical `/api/v1/ask` call is meaningfully faster than
      the first
- [ ] A cache miss and a cache hit both show up as traces in Langfuse
      (if you've got it enabled)
- [ ] Killing Redis doesn't break `/api/v1/ask` — it should just get
      slower (every call becomes a miss)

## Common pitfalls

- Hashing an unsorted dict of params — see the "stable cache key" note
  above; this causes cache misses that look like "caching isn't working"
  but are actually "the key changes every time."
- Letting a Langfuse failure raise and break the actual response —
  tracing should be wrapped so it can never take down a working request.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week6/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week6/week6_cache_testing.ipynb`
- Blog post: [Production-ready RAG: Monitoring & Caching](https://jamwithai.substack.com/p/production-ready-rag-monitoring-and)

Previous: [Week 5](week5.md) · Next: [Week 7 — Agentic RAG](week7.md)
