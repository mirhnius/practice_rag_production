"""
Week 2 — pipeline orchestrator.

Wires ArxivClient -> PDFParserService -> PaperRepository into one call so
routers (and, eventually, an Airflow DAG if you build one) don't need to
know the individual steps. This is the "MetadataFetcher" the Week 2
README calls the main orchestrator.
"""

from sqlalchemy.orm import Session

from src.repositories.paper import PaperRepository
from src.schemas.paper import PaperCreate
from src.services.arxiv.client import ArxivClient
from src.services.pdf_parser.parser import PDFParserService


class MetadataFetcher:
    def __init__(self, arxiv_client: ArxivClient, pdf_parser: PDFParserService) -> None:
        self.arxiv_client = arxiv_client
        self.pdf_parser = pdf_parser

    def fetch_and_process_papers(
        self,
        session: Session,
        max_results: int = 15,
        process_pdfs: bool = True,
    ) -> dict:
        """Fetch papers, optionally parse their PDFs, and store everything.

        TODO:
        - papers = self.arxiv_client.fetch_papers(max_results=max_results)
        - repo = PaperRepository(session)
        - counters = {"papers_fetched": len(papers), "pdfs_downloaded": 0,
          "pdfs_parsed": 0, "papers_stored": 0, "errors": []}
        - for each paper:
            - try: build a PaperCreate from it (raw_text=None initially)
            - if process_pdfs: try downloading + parsing the PDF, and if
              that succeeds, set raw_text and bump the counters
            - repo.upsert(paper_create); bump papers_stored
            - except Exception as exc: append str(exc) to errors and
              continue to the next paper — one bad paper must not abort
              the batch
        - return counters (this is exactly what
          scripts/week2_test_arxiv_pipeline.py prints)
        """
     
        papers = self.arxiv_client.fetch_papers(max_results=max_results)
        paper_repo = PaperRepository(session)
        counters = {
            "papers_fetched": len(papers),
            "pdfs_downloaded": 0,
            "pdfs_parsed": 0,
            "papers_stored": 0,
            "errors": [],
        }
        for paper in papers:
            try:
                paper_create = PaperCreate(**paper.model_dump())
                if process_pdfs:
                    try:
                        pdf_path = self.arxiv_client.download_pdf(paper)
                        counters["pdfs_downloaded"] += 1
                        pdf_parsed = self.pdf_parser.parse_pdf(pdf_path)
                        if pdf_parsed:
                            paper_create.raw_text = pdf_parsed.raw_text
                            counters["pdfs_parsed"] += 1
                    except Exception as exc:
                        counters["errors"].append(f"{paper.arxiv_id} (PDF): {exc}")
                paper_repo.upsert(paper_create)
                counters["papers_stored"] += 1  
            except Exception as exc:
                counters["errors"].append(f"{paper.arxiv_id}: {exc}")
        return counters
              
