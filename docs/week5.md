# Week 5 — Complete RAG Pipeline

## What you're building this week

The part that makes this a "RAG" system rather than just a search
engine: retrieved chunks get turned into a prompt, and a local LLM
(via Ollama) generates an actual answer instead of a list of documents.

## Concepts you need before writing code

### Why the prompt has to stay small

Every extra token in the prompt costs generation time — the course
measured an **80% reduction in prompt size → 6x faster responses**
(120s down to 15-20s) just from cutting redundant metadata out of the
context. Concretely: don't dump the full JSON of each chunk (arxiv_id,
title, authors, score, section_name, chunk_text, published_date...) into
the prompt. Include only what the LLM needs to answer and cite:
something like `[2508.18563] <chunk text>`. Everything else (score,
section name) is useful to *you* for debugging, not to the model for
answering.

### System prompt vs. user content

`SYSTEM_PROMPT` in `src/services/ollama/prompts.py` sets the LLM's
*behavior* — answer only from the given excerpts, cite by arXiv ID,
don't hallucinate, stay under 300 words. The actual context + question
is separate, assembled fresh per request in `build_rag_prompt`. Keeping
these separate means you can tune "how the model behaves" without
touching "how a specific request is built."

### Streaming: same pipeline, different delivery

`/api/v1/ask` waits for the full answer, then returns it — simple, but
the user stares at nothing for 15-20 seconds. `/api/v1/stream` sends
tokens as they're generated using **Server-Sent Events**, so the user
sees the first words in ~2-3 seconds even though total generation time
is the same. Under the hood this is the *same* retrieval and prompt
assembly — the only difference is `OllamaClient.generate` (waits, then
returns one string) vs. `generate_stream` (a generator that `yield`s
pieces as Ollama produces them, which `StreamingResponse` sends to the
client incrementally).

## Files to implement, in order

1. **`src/config.py`** — add `ollama_host`, `ollama_model`.
2. **`src/services/ollama/client.py`** — `generate` (one blocking POST to
   Ollama's `/api/generate` with `"stream": False`) and `generate_stream`
   (`"stream": True`, iterate `response.iter_lines()`, `yield` each
   piece).
3. **`src/services/ollama/prompts.py`** — `build_rag_prompt`, following
   the "keep it small" guidance above.
4. **`src/routers/ask.py`** — `/api/v1/ask` and `/api/v1/stream`, each
   doing retrieve (reuse Week 4's hybrid search) → build prompt →
   generate.

## Walking through `scripts/week5_test_rag.py`

1. Embed a fixed test query and run hybrid search against the chunks you
   indexed in Week 4.
2. Build the RAG prompt from those chunks.
3. Generate a full (non-streaming) answer and print it.
4. Generate the *same* answer via `generate_stream`, joining the pieces
   back together — proves the streaming code path works even though the
   script itself doesn't need to show tokens arriving live.
5. Bonus: hit your own `/api/v1/ask` endpoint if it's running.

## Success criteria

- [ ] `ollama_client.generate(prompt)` returns a real, on-topic answer
      (not an error, not a refusal to answer because the prompt was
      malformed)
- [ ] The answer references the paper(s) actually retrieved, not
      generic knowledge unrelated to your indexed papers
- [ ] `generate_stream` produces the same kind of answer as `generate`,
      just delivered incrementally
- [ ] `/api/v1/ask` and `/api/v1/stream` both work over HTTP once you've
      wired the router

## Common pitfalls

- A model that isn't pulled yet — `docker exec rag-ollama ollama pull llama3.2:1b`
  before this will do anything.
- A prompt so bloated with metadata that generation crawls — if a call
  takes way longer than the course's ~15-20s baseline, look at what
  you're actually putting in the prompt before assuming Ollama itself is
  slow.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week5/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week5/week5_complete_rag_system.ipynb`
- Blog post: [The Complete RAG System](https://jamwithai.substack.com/p/the-complete-rag-system)

Previous: [Week 4](week4.md) · Next: [Week 6 — Monitoring & Caching](week6.md)
