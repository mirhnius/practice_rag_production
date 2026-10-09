# Week 2 — Data Ingestion Pipeline

## What you're building this week

A pipeline that: asks arXiv's public API for recent papers → downloads
their PDFs → parses each PDF into structured text → stores everything in
Postgres. This is the raw material every later week searches, chunks,
embeds, and eventually asks an LLM about — if this week's data is messy,
everything downstream inherits that mess, so it's worth doing carefully.

## Concepts you need before writing code

### Calling arXiv politely

arXiv's API (`https://export.arxiv.org/api/query`) is free and has no
API key, which is exactly why it asks callers to self-limit: **no more
than one request every 3 seconds**, or they'll start blocking you. So
`ArxivClient` isn't just "make an HTTP request" — it has to *remember
when it last called* and sleep the remainder of 3 seconds if you call it
again too soon. That's the `_respect_rate_limit` method.

You also want retries: arXiv occasionally returns a `503` under load.
The fix isn't to treat that as a hard failure — retry 2-3 times with a
short backoff (wait longer each attempt) before giving up.

The response itself is an **Atom XML feed**, not JSON. Each paper is an
`<entry>` with children like `<id>`, `<title>`, `<summary>` (the
abstract), one `<author><name>` per author, `<category term="cs.AI">`
per category, `<published>`, and a `<link rel="related" type="application/pdf">`
pointing at the PDF. Python's built-in `xml.etree.ElementTree` is enough
to parse this — no extra dependency needed. Watch out for Atom's XML
namespace (`{http://www.w3.org/2005/Atom}entry`, not just `entry`).

### Turning a PDF into text you can actually search

A raw PDF is just glyph positions on a page — there's no built-in
concept of "this is the introduction, this is a table." **Docling**
does the hard work of reconstructing that structure: headings, body
text, tables. You care about this now because Week 4's chunker will
chunk *by section* rather than blindly cutting every 600 words, which
only works if you've kept section boundaries around.

Some PDFs will fail to parse — scanned images, unusual layouts,
whatever. That's expected (the course sees roughly an 80-90% success
rate on real arXiv PDFs), so `parse_pdf` should catch its own exceptions
and return `None` rather than raising, so one bad paper doesn't take
down a whole batch job.

### Why three layers instead of one (model / schema / repository)

- **`models/paper.py`** — the SQLAlchemy table definition. This is *only*
  about what Postgres stores.
- **`schemas/paper.py`** — three separate Pydantic classes
  (`ArxivPaperMetadata`, `PaperCreate`, `PaperOut`) instead of one,
  because each represents data at a different point in the pipeline:
  fresh off the arXiv API, ready to write to the DB, and safe to hand
  back over the API. Collapsing them into one class works today but
  breaks the moment the DB schema and the API response need to diverge
  (e.g. you never want to expose `raw_text` in a list endpoint).
- **`repositories/paper.py`** — the only place allowed to write SQLAlchemy
  queries against `Paper`. Routers and services call
  `PaperRepository.upsert(...)`, never `session.query(Paper)` directly.
  That's what keeps "how we query" in one place instead of copy-pasted
  across every router.

**Upsert**, specifically: re-running the pipeline on the same date range
will re-fetch papers you already have. Rather than crash on a duplicate
`arxiv_id` or silently make a second row, upsert means "update it if it
exists, insert it if it doesn't" — look up by `arxiv_id` first, then
branch.

### Tables don't create themselves

Writing `class Paper(Base)` only *describes* a table in Python. Postgres
has no `papers` table until something sends it a `CREATE TABLE`.
SQLAlchemy does that for you with `Base.metadata.create_all(bind=engine)`:
it looks at every model registered on `Base` and creates the ones that
don't exist yet, skipping any that do — so it's safe to run repeatedly.
That's what `init_db()` in `src/db/session.py` does (it's provided for
you), and the Week 2 script calls it as Step 0. Without it, every
`upsert` fails with `relation "papers" does not exist`.

Two things worth knowing:

- **Registration happens on import.** `Paper` only joins `Base.metadata`
  when `models/paper.py` is actually imported. If nothing imported it,
  `create_all` creates zero tables and says nothing. That's why
  `init_db()` imports the model *inside the function*: a top-level import
  would be circular, because the model file imports `Base` from
  `session.py`.
- **`create_all` never changes an existing table.** If you add or rename a
  column after the table exists, nothing happens — Postgres keeps the old
  shape. For a learning project the simple fix is to drop the table
  (`DROP TABLE papers;`) and run again. Real projects use a migration
  tool (Alembic) for this.

## Files to implement, in order

1. **`src/config.py`** — add `postgres_database_url`, `arxiv_base_url`,
   `arxiv_search_category`, `arxiv_max_results`, `arxiv_rate_limit_delay`,
   `arxiv_pdf_cache_dir` (the TODO comment already there names these).
2. **`src/db/session.py`** — `engine`, `SessionLocal`, and `get_session()`.
   The pattern to know: `get_session()` is a *context manager*
   (`with get_session() as session:`) that commits if the `with` block
   finishes cleanly and rolls back if it raises — that's why the body is
   a try/except/finally around a single `yield`. The file also has
   `init_db()`, which is already written — see "Tables don't create
   themselves" above.
3. **`src/models/paper.py`** — the columns (see the TODO list in the
   file; nothing tricky, just SQLAlchemy `Mapped[...]` column
   declarations).
4. **`src/schemas/paper.py`** — the three Pydantic classes described above.
5. **`src/repositories/paper.py`** — `upsert`, `get_by_arxiv_id`,
   `list_papers`.
6. **`src/services/arxiv/client.py`** — `_respect_rate_limit`,
   `fetch_papers`, `download_pdf`.
7. **`src/services/pdf_parser/parser.py`** — `parse_pdf`, using Docling's
   `DocumentConverter`.
8. **`src/services/metadata_fetcher.py`** — `fetch_and_process_papers`,
   which just calls the pieces above in order and collects errors instead
   of crashing on the first bad paper.
9. **`src/routers/papers.py`** — thin `GET` endpoints over the repository.

## Walking through `scripts/week2_test_arxiv_pipeline.py`

The script is a **plain, top-to-bottom sequence of steps** — no helper
framework, nothing hidden. Each step is a clearly labeled block that
calls straight into the file above it in the list, in order:

0. Create the `papers` table if it's missing (`init_db()`). This runs
   first so a missing table or an unreachable Postgres fails immediately,
   before any slow network or PDF work.
1. Build an `ArxivClient` from settings, call `fetch_papers(max_results=2)`.
2. Download the PDF for the first paper (`download_pdf`).
3. Parse it (`parse_pdf`).
4. Store that one paper in Postgres (`PaperRepository.upsert`).
5. Run the *whole* pipeline end to end via `MetadataFetcher`, on a fresh
   pair of papers, with PDF processing turned on.

If a step's underlying function isn't implemented yet, Python raises
`NotImplementedError` and the script stops right there — the traceback
tells you exactly which file and line to go fill in next. That mirrors
the notebook: cell 8 couldn't run if cell 7 hadn't produced `papers`
either.

## Success criteria

- [ ] The `papers` table exists — check with
      `docker compose exec postgres psql -U rag_user -d rag_db -c '\dt papers'`
- [ ] `fetch_papers()` returns real `ArxivPaperMetadata` objects
- [ ] A PDF downloads and Docling parses it into sections
- [ ] A paper round-trips through Postgres (`upsert` then `get_by_arxiv_id`)
- [ ] The full `MetadataFetcher` run reports `papers_stored > 0` with no
      unhandled exceptions, even if a PDF or two fails to parse

## Common pitfalls

- **arXiv 503s** — normal, not a bug in your code; retry logic should
  absorb it.
- **PDF parse failures** — normal too; `parse_pdf` should return `None`,
  not raise, so `MetadataFetcher` can skip that paper and continue.
- **Forgetting the Atom namespace** when parsing XML — `entry` won't
  match anything; you need the full `{http://www.w3.org/2005/Atom}entry`.
- **`relation "papers" does not exist`** — the table was never created.
  Run the script (Step 0 calls `init_db()`), or call `init_db()` yourself.
- **Changed a column but nothing changed in Postgres** — `create_all`
  never alters an existing table. Drop it (`DROP TABLE papers;`) and
  re-run so it's recreated with the new shape.

## If you want the original course material too

- Course README: `../production-agentic-rag-course/notebooks/week2/README.md`
- Course notebook (optional, for reference only):
  `../production-agentic-rag-course/notebooks/week2/week2_arxiv_integration.ipynb`
- Blog post: [Building Data Ingestion Pipelines for RAG](https://jamwithai.substack.com/p/bringing-your-rag-system-to-life)

Previous: [Week 1](week1.md) · Next: [Week 3 — Keyword Search](week3.md)
