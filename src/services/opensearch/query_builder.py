"""
Week 3 — BM25 query builder.

Keeping query construction in its own module (instead of inline in
client.py) is what the course calls the "Query Builder Pattern" — each
query shape is testable on its own, and client.py stays focused on
transport rather than query DSL.
"""


def build_match_query(query: str, size: int = 10, from_: int = 0) -> dict:
    """A multi-field BM25 query with field boosting.

    TODO: return an OpenSearch query body using `multi_match` across
    title (boost ~3x), abstract (boost ~2x), and raw_text (boost 1x).
    Include "size" and "from" for pagination, and a "highlight" block on
    title/abstract so callers can show *why* a result matched.
    """
    raise NotImplementedError


def build_filtered_query(
    query: str,
    categories: list[str] | None = None,
    size: int = 10,
) -> dict:
    """Same idea as build_match_query, plus an optional category filter.

    TODO: wrap the multi_match in a `bool` query; if `categories` is
    given, add a `"filter": [{"terms": {"categories": categories}}]`
    clause (filters narrow the result set without affecting the score).
    """
    raise NotImplementedError
