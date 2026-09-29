"""
Week 7 — agent state.

The shared state object every LangGraph node reads from and writes to as
the workflow runs. Modeled after the course's workflow: guardrail ->
retrieve -> grade -> (rewrite -> retrieve -> grade again, if needed) ->
generate (or straight to out_of_scope if the guardrail rejects the query).
"""

from typing import TypedDict


class GraphState(TypedDict, total=False):
    query: str
    rewritten_query: str
    chunks: list[dict]
    is_relevant: bool
    in_scope: bool
    retrieval_attempts: int
    answer: str
    reasoning_steps: list[str]
