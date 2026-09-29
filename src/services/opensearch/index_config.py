"""
Week 3 — OpenSearch index configuration.

Defines the mapping for the `arxiv-papers` index: which fields exist,
their types, and which analyzer powers full-text relevance scoring. This
is what makes BM25 search on `title`/`abstract` behave sensibly (English
stemming, stopword handling, ...) instead of doing exact string matches.
"""

INDEX_NAME = "arxiv-papers"
CHUNK_INDEX_NAME = "arxiv-papers-chunks"

# TODO: define the mapping OpenSearch expects, roughly:
#
# INDEX_MAPPING = {
#     "settings": {
#         "analysis": {"analyzer": {"default": {"type": "english"}}}
#     },
#     "mappings": {
#         "properties": {
#             "arxiv_id": {"type": "keyword"},
#             "title": {"type": "text"},
#             "abstract": {"type": "text"},
#             "authors": {"type": "keyword"},
#             "categories": {"type": "keyword"},
#             "published_date": {"type": "date"},
#             "pdf_url": {"type": "keyword"},
#         }
#     },
# }
INDEX_MAPPING: dict = {}  # TODO

# TODO (Week 4): CHUNK_INDEX_MAPPING — same idea as INDEX_MAPPING, plus:
# - chunk_id: keyword, arxiv_id: keyword, section_name: keyword, chunk_text: text
# - embedding: {"type": "knn_vector", "dimension": 1024}
# and "settings": {"index": {"knn": True}} to turn on k-NN search for this index.
CHUNK_INDEX_MAPPING: dict = {}  # TODO
