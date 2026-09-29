"""
Week 5 — RAG prompt assembly.

The course found trimming this prompt (dropping redundant metadata from
each chunk) cut generation time by ~80% with no real quality loss —
keep it tight.
"""

SYSTEM_PROMPT = """You are a research assistant answering questions using \
only the provided paper excerpts. If the excerpts don't contain the \
answer, say so instead of guessing. Cite papers by arXiv ID. Keep answers \
under 300 words."""


def build_rag_prompt(query: str, chunks: list[dict]) -> str:
    """Assemble the final prompt sent to the LLM.

    TODO:
    - format each chunk as something like
      f"[{chunk['arxiv_id']}] {chunk['chunk_text']}"
    - join them under a "Context:" heading, followed by
      f"Question: {query}\\nAnswer:"
    - prefix the whole thing with SYSTEM_PROMPT (or, if you move to a
      chat-style endpoint later, pass SYSTEM_PROMPT as a separate
      system message instead of concatenating it)
    """
    raise NotImplementedError
