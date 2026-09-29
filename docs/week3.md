# Week 3 — Keyword Search Foundation (BM25)

## What you're building this week

Every paper you stored in Week 2 goes into OpenSearch, and you build a
search endpoint that ranks results by relevance — no AI involved yet.
This might feel like a detour before "real" semantic search, but it's
the foundation Week 4 *adds* vector search on top of, not replaces —
most production RAG systems still lean on keyword search for exact
terms, paper IDs, and acronyms that embeddings are surprisingly bad at.

## Concepts you need before writing code

### What BM25 actually does

BM25 scores how well a document matches a query using two ideas: **term
frequency** (a document mentioning "transformer" 5 times is probably
more about transformers than one mentioning it once — but with
diminishing returns, so 50 mentions isn't 10x more relevant than 5) and
**inverse document frequency** (a rare word like "attention" tells you
more than a common word like "the", which every document sitting in the
index contains anyway). You don't implement the BM25 math yourself —
OpenSearch does that — but knowing *why* a result scores higher helps
you debug when your search returns the wrong papers.

### Analyzers: why raw text search feels dumb without them

Without an analyzer, searching "learning" wouldn't match a document
containing "learn" or "learns" — literal substring/token matching only.
The **english analyzer** applies stemming (learning → learn), lowercases
everything, and drops stopwords (the, a, of). That's why
`src/services/opensearch/index_config.py` sets an analyzer in the index
settings rather than leaving OpenSearch's defaults — it's the difference
between search that feels smart and search that feels broken.

### Mapping: telling OpenSearch what your fields *are*

A mapping is a schema for your index: `title` and `abstract` should be
`text` (analyzed, searchable by meaning), while `arxiv_id` and
`categories` should be `keyword` (exact-match only — you never want
"cs.AI" to fuzzy-match "cs.LG"). Get this wrong and either search stops
working, or filters stop being exact.

### Query vs. filter — a distinction that matters

In a `bool` query, `must`/`should` clauses **affect the relevance
score**; `filter` clauses **only narrow the result set**, contributing
zero to scoring and running faster because OpenSearch can cache them.
Category filtering belongs in `filter`, not `must` — you don't want
"is this cs.AI" affecting how *relevant* a result looks, only whether
it's included at all.

### Why a separate query_builder.py

Keeping query-dict construction out of `client.py` (the course calls
this the "Query Builder Pattern") means you can unit-test
`build_filtered_query("neural", ["cs.AI"])` in isolation — check the
dict shape is right — without spinning up OpenSearch at all.

## Files to implement, in order

1. **`src/config.py`** — add `opensearch_host`, `opensearch_index_name`.
2. **`src/services/opensearch/index_config.py`** — `INDEX_MAPPING`: field
   types + the english analyzer, as described above.
3. **`src/services/opensearch/query_builder.py`** — `build_match_query`
   (multi-field BM25 with boosting: title matters more than abstract,
   abstract more than body) and `build_filtered_query` (same, plus an
   optional category filter).
4. **`src/services/opensearch/client.py`** — `health_check`,
   `create_index_if_missing`, `index_paper`, `search`. This wraps the
   raw `opensearch-py` library so nothing else in the app imports
   `OpenSearch` directly.
5. **`src/routers/search.py`** — `GET /api/v1/search?q=...`, a thin
   wrapper over `OpenSearchClient.search`.

## Walking through `scripts/week3_test_search.py`

Plain top-to-bottom steps, calling straight into the files above:

1. Health-check OpenSearch — stops here if it's not reachable.
2. Create the `arxiv-papers` index (safe to call repeatedly — it should
   no-op if the index already exists).
3. Pull every paper you stored in Postgres during Week 2 and index each
   one into OpenSearch.
4. Run a plain search for `"learning"` and print the ranked results with
   scores.
5. Run the same kind of search but filtered to `categories=["cs.AI"]`.
6. As a bonus, try your own `/api/v1/search` HTTP endpoint if you've got
   `uv run uvicorn src.main:app --reload --port 8100` running in another
   terminal — this step is skipped, not failed, if the app isn't up.

## Success criteria

- [ ] The index exists with the mapping you defined (check via
      `curl http://localhost:9200/arxiv-papers/_mapping`)
- [ ] Every paper from Postgres is indexed
- [ ] A search for a real word from one of your papers' abstracts
      returns that paper, ranked with a sensible score
- [ ] Filtering by category actually narrows results, without changing
      which result ranks first among the ones that pass the filter

## Common pitfalls

- Forgetting to call `create_index_if_missing()` before indexing —
  OpenSearch will auto-create an index with a guessed (wrong) mapping if
  you index into one that doesn't exist yet, and you'll be stuck with a
  bad mapping until you delete and recreate it.
- Putting category filtering in `must` instead of `filter` — it'll
  "work" but skew relevance scores in a way that's hard to notice until
  results look subtly wrong.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week3/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week3/week3_opensearch.ipynb`
- Blog post: [The Search Foundation Every RAG System Needs](https://jamwithai.substack.com/p/the-search-foundation-every-rag-system)

Previous: [Week 2](week2.md) · Next: [Week 4 — Chunking & Hybrid Search](week4.md)
