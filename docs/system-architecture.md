# System Architecture

This diagram shows the main layers and infrastructure used by the project.

```mermaid
flowchart TB
    Client[API client] --> Routers[FastAPI routers]
    Routers --> Services[Application services]
    Services --> Repositories[Repositories]
    Repositories --> Session[SQLAlchemy session]
    Session --> Postgres[(PostgreSQL)]

    Services --> Arxiv[arXiv API]
    Services --> Docling[Docling PDF parser]
    Services --> OpenSearch[(OpenSearch)]
    Services --> Ollama[Ollama]
    Services --> Redis[(Redis)]
```

## Responsibilities

- **Routers** receive HTTP requests and return validated responses.
- **Services** coordinate application workflows.
- **Repositories** contain database queries and persistence logic.
- **Models** describe database tables.
- **Schemas** describe validated input and output data.
- **Clients** isolate communication with external services.
