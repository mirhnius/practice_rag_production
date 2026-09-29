# Week 7 — Agentic RAG with LangGraph

## What you're building this week

Every prior week's pipeline is a fixed pipe: query → retrieve → generate,
always, no matter what. This week you replace that straight line with a
graph that can make decisions: skip retrieval for a trivial question,
check whether what it retrieved is actually relevant, and rewrite a bad
query and try again instead of just answering badly.

## Concepts you need before writing code

### A graph instead of a straight line

LangGraph models your pipeline as a state machine: **nodes** are steps
(functions), **edges** connect them, and some edges are **conditional** —
"go to node A if X, node B otherwise" based on the current state. The
state itself (`GraphState` in `src/services/agents/state.py`) is a
dict-like object every node reads from and returns updates to; LangGraph
merges each node's return value into the running state before calling
the next node.

The shape you're building:

```
START -> guardrail --(out of scope)--> out_of_scope -> END
                 \--(in scope)-------> retrieve -> grade
                                          (relevant)-------> generate -> END
                                          (not relevant,
                                           attempts left)---> rewrite -> retrieve -> grade -> ...
                                          (not relevant,
                                           out of attempts)-> generate -> END  (best effort)
```

### Why a guardrail node

Not every message deserves a full retrieve-and-generate cycle. "What's
2+2?" or "write me a poem" don't need this system's paper index at
all — a guardrail asks the LLM a cheap classification question first
("is this in-scope for a research assistant over arXiv papers?") and
routes obviously-unrelated queries straight to a canned decline,
skipping retrieval entirely. This is also what makes trivial questions
answer in ~2-5s instead of ~15-20s: no retrieval means no embedding call
and no search round-trip.

### Why grade what you retrieved

Search can return low-quality matches, especially for a vague query.
Grading — asking the LLM "do these chunks actually answer this
question?" — is what tells the graph whether it's safe to generate an
answer, or whether it should try again with a better query instead of
confidently answering from irrelevant context.

### Query rewriting and the loop

If grading says "not relevant," rewriting asks the LLM to restate the
original query more specifically, then loops back to `retrieve`. This
can't loop forever — `retrieval_attempts` in the state caps it (2 in
this scaffold), after which the graph falls through to `generate` anyway
and answers as best it can rather than getting stuck.

### Reasoning transparency

Every node appends a short string to `reasoning_steps` in the state
(e.g. `"Retrieved documents"`, `"Not relevant, rewriting query"`). By the
time the graph reaches `END`, that list is a readable trace of every
decision the agent made — which is what the API response exposes,
turning what would otherwise be a black box into something you can
actually debug.

## Files to implement, in order

1. **`src/config.py`** — add `telegram_bot_token` (only needed if you
   build the optional Telegram bot at the end).
2. **`src/services/agents/state.py`** — already fully defined
   (`GraphState`); read it, nothing to implement.
3. **`src/services/agents/nodes.py`** — six small functions:
   `guardrail_node`, `retrieve_node`, `grade_documents_node`,
   `rewrite_query_node`, `generate_answer_node`, `out_of_scope_node`.
   Each one is small on purpose — if you find yourself writing more than
   ~20-30 lines in one, it's probably doing two jobs.
4. **`src/services/agents/graph.py`** — `build_agentic_rag_graph`: wire
   the nodes above into a `StateGraph` with the conditional edges shown
   in the diagram.
5. **`src/routers/agentic_ask.py`** — `POST /api/v1/ask-agentic`, which
   builds the graph and calls `.invoke(...)` on it.
6. **`src/services/telegram_bot.py`** (optional/stretch) — only build
   this once the endpoint above works and you want a mobile front-end.

## Walking through `scripts/week7_test_agentic_rag.py`

Builds the graph once, then runs it against three scenarios the course
specifically calls out, printing the answer and the full
`reasoning_steps` list for each:

1. **Out-of-scope rejection** — `"Write me a poem about cats"` should
   route straight to `out_of_scope` and never call `retrieve`.
2. **Successful retrieval** — a real research question should retrieve,
   grade as relevant, and generate directly.
3. **Vague query, may need a rewrite** — `"Tell me about ML stuff"`
   might grade as not-relevant on the first pass and trigger a rewrite +
   second retrieval before generating.

## Success criteria

- [ ] Scenario 1's `reasoning_steps` shows it never retrieved
- [ ] Scenario 2 answers correctly with sources, in one retrieval attempt
- [ ] Scenario 3 either answers well on the first try, or its
      `reasoning_steps` shows a rewrite happened before it did
- [ ] `retrieval_attempts` never exceeds your configured max — confirms
      the loop actually terminates instead of hanging

## Common pitfalls

- A conditional edge function that doesn't return one of the exact
  string keys you registered in `add_conditional_edges` — LangGraph will
  raise a fairly opaque error; double check the mapping dict's keys
  match what your function returns.
- Forgetting to increment `retrieval_attempts` in `retrieve_node` — that
  breaks the loop's exit condition and Week 7's whole "don't loop
  forever" guarantee.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week7/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week7/week7_agentic_rag.ipynb`
- Blog post: [Agentic RAG with LangGraph and Telegram](https://jamwithai.substack.com/p/agentic-rag-with-langgraph-and-telegram)

Previous: [Week 6](week6.md) · Back to [ROADMAP](../ROADMAP.md)
