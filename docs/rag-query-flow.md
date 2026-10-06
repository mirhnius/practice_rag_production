# RAG Query Flow

The later weeks add retrieval and generation on top of the ingestion
foundation.

```mermaid
flowchart LR
    User[User question] --> AskRouter[Ask router]
    AskRouter --> RAG[RAG service]
    RAG --> Query[Query builder]
    Query --> Keyword[Keyword search]
    Query --> Vector[Vector search]
    Keyword --> Search[(OpenSearch)]
    Vector --> Search
    Search --> Context[Relevant paper chunks]
    User --> Prompt[Prompt builder]
    Context --> Prompt
    Prompt --> LLM[Ollama LLM]
    LLM --> Answer[Grounded answer]
```

## Two Halves of the Project

```text
Data engineering:
    collect -> parse -> store -> index

AI engineering:
    retrieve -> build context -> generate -> evaluate
```
