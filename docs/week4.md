# Week 4 — Chunking & Hybrid Search

## What you're building this week

Two upgrades to Week 3's search: (1) instead of searching whole papers,
you search *chunks* of papers, so results point at the specific
paragraph that answers a question rather than a 10-page PDF; (2) instead
of keyword-only matching, you add vector (semantic) search and combine
it with BM25 using **Reciprocal Rank Fusion (RRF)**.

## Concepts you need before writing code

### Why chunk at all?

Two reasons. First, an LLM (Week 5) has a limited context window — you
can't stuff a whole paper into a prompt, so you need small, relevant
pieces. Second, embeddings work better on focused text: a single vector
representing an entire 8,000-word paper blurs together the introduction,
methodology, and conclusion into a mushy average that doesn't match
anything precisely. A vector representing one paragraph about attention
mechanisms actually captures "this is about attention mechanisms."

### Why overlap chunks

If chunk boundaries land in the middle of an idea — "...as shown in
Figure 3, the model" | "achieves 94% accuracy..." — split right at the
critical fact, both halves lose meaning. A 100-word overlap between
consecutive chunks means that boundary sentence exists whole in at least
one chunk. It's a small tax on storage for a real gain in retrieval
quality.

### What an embedding actually is

An embedding is a list of numbers (1024 of them, for the Jina model this
course uses) that represents a piece of text's *meaning* as a point in
high-dimensional space. Texts with similar meaning end up as nearby
points — "the model achieves high accuracy" and "the classifier performs
well" land close together even though they share almost no words in
common. That's what lets vector search find "attention mechanism" when
someone searches "how transformers decide what to focus on" — no
keyword overlap needed, BM25 alone would miss it entirely.

### Reciprocal Rank Fusion (RRF), worked through with numbers

You now have two independent rankings for the same query — one from
BM25, one from vector search — and need to merge them into one list.
RRF's idea: for each document, look at *what rank it got in each list*
(1st, 2nd, 3rd...), not the raw score (BM25 scores and cosine
similarities aren't even on the same scale, so comparing them directly
is meaningless). A document's RRF score is:

```
score = sum over every ranking it appears in of  1 / (k + rank)
```

with `k = 60` conventionally. Worked example: paper X ranks **#1** in
BM25 and **#3** in vector search:

```
score(X) = 1/(60+1) + 1/(60+3) = 0.01639 + 0.01587 = 0.03226
```

Paper Y ranks **#2** in BM25 but doesn't appear in the vector results at
all:

```
score(Y) = 1/(60+2) = 0.01613
```

X beats Y — it shows up strongly in *both* rankings, which is exactly
the "best of both worlds" behavior you want: keyword precision when
terms match exactly, semantic recall when they don't.

## Files to implement, in order

1. **`src/config.py`** — add `chunk_size`, `chunk_overlap_size`,
   `chunk_min_size`, `jina_api_key`.
2. **`src/services/opensearch/index_config.py`** — `CHUNK_INDEX_MAPPING`:
   like Week 3's mapping, plus a `knn_vector` field for the embedding
   (1024 dimensions) and `"index": {"knn": True}` in settings to turn on
   vector search for this index.
3. **`src/services/indexing/text_chunker.py`** — `chunk_paper` and the
   `_chunk_text` helper: walk a section's words in overlapping windows
   (see the walked-through overlap example above).
4. **`src/services/embeddings/jina_client.py`** — `embed` / `embed_query`:
   a plain HTTP POST to Jina's API.
5. **`src/services/opensearch/client.py`** — the Week 4 methods:
   `create_chunk_index_if_missing`, `index_chunk`, `search_vector`
   (k-NN query), `search_hybrid` (BM25 + vector + RRF, per the formula
   above).
6. **`src/services/indexing/hybrid_indexer.py`** — `index_paper_chunks`:
   chunk → embed → index, glued together.
7. **`src/routers/hybrid_search.py`** — `POST /api/v1/hybrid-search`.

## Walking through `scripts/week4_test_hybrid_search.py`

1. Pull a paper from Postgres that has `raw_text` set (i.e. one whose
   PDF parsed successfully back in Week 2).
2. Chunk it and print how many chunks came out.
3. Embed a test query with Jina and confirm you get a 1024-dim vector back.
4. Create the chunk index.
5. Run the full `HybridIndexer` on that paper: chunk, embed every chunk,
   index every chunk.
6. Search the same query three ways — BM25-only, vector-only, hybrid —
   so you can see the different result sets side by side.
7. Bonus: hit your own `/api/v1/hybrid-search` endpoint if it's running.

## Success criteria

- [ ] Chunking a real paper produces multiple overlapping chunks, not
      one giant blob or hundreds of tiny fragments
- [ ] `embed_query` returns a 1024-length list of floats
- [ ] `search_vector` returns results ranked by semantic similarity, even
      for a query with none of the same words as the source text
- [ ] `search_hybrid` returns a single merged ranking, and a doc that
      scores well in both BM25 and vector search should rank at the top

## Common pitfalls

- Forgetting `"index": {"knn": True}` in the chunk index settings — k-NN
  queries will fail with a mapping error until this is set, and it can't
  be changed on an index that already exists (you'll need to delete and
  recreate it).
- RRF on raw scores instead of ranks — BM25 scores are unbounded and
  vector similarity is roughly 0-1, so combining them directly makes one
  algorithm dominate for no principled reason. Rank-based fusion avoids
  that entirely.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week4/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week4/week4_hybrid_search.ipynb`
- Blog post: [The Chunking Strategy That Makes Hybrid Search Work](https://jamwithai.substack.com/p/chunking-strategies-and-hybrid-rag)

Previous: [Week 3](week3.md) · Next: [Week 5 — Complete RAG Pipeline](week5.md)
