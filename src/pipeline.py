import os
from pathlib import Path
from typing import Optional

import pyalex

from .database import get_neon_connection, create_papers_table
from .fetch_recent_ai_papers import (
    get_ai_concept_id,
    fetch_recent_ai_works,
    save_works_to_timestamped_file,
)
from .load_papers import load_works_from_file, upsert_paper, ensure_schema
from .run_data_quality import SUMMARY_SQL


class AIPapersPipeline:
    """
    End-to-end pipeline for:
    - Querying OpenAlex via PyAlex for recent AI papers
    - Ensuring the database schema exists
    - Loading papers into Postgres with deduplication
    - Running a data quality summary report
    """

    def __init__(self, days: int = 30, title_search: Optional[str] = "artificial intelligence"):
        self.days = days
        self.title_search = title_search

    def _configure_openalex(self) -> None:
        api_key = os.getenv("OPENALEX_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Please set the OPENALEX_API_KEY environment variable before running the pipeline."
            )
        pyalex.config.api_key = api_key

    def fetch_and_save_recent_papers(self) -> Path:
        """
        Query OpenAlex for recent AI papers and save them to a timestamped JSON file.

        Returns the path to the saved JSON file.
        """
        self._configure_openalex()

        concept_id = get_ai_concept_id()
        works, meta = fetch_recent_ai_works(
            concept_id=concept_id,
            days=self.days,
            title_search=self.title_search,
        )

        output_path = save_works_to_timestamped_file(works, meta)
        print(
            f"Saved {len(works)} AI works from the last {self.days} days to {output_path} "
            f"(expected_count={meta['expected_count']})"
        )
        return output_path

    def load_papers_into_db(self, json_path: Path) -> None:
        """
        Load works from the given JSON file into the database.
        Ensures schema and performs upserts into the papers-related tables.
        """
        works = load_works_from_file(json_path)
        print(f"Loading {len(works)} works from {json_path} into the database...")

        conn = get_neon_connection()
        try:
            # Ensure tables exist (papers and related tables)
            ensure_schema(conn)

            for i, work in enumerate(works, start=1):
                upsert_paper(conn, work)
                if i % 100 == 0:
                    print(f"Upserted {i} papers...")

            print(f"Finished loading {len(works)} papers into the database.")
        finally:
            conn.close()

    def run_data_quality_report(self) -> None:
        """
        Run the summary data quality report against the papers table
        and print the results.
        """
        conn = get_neon_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SUMMARY_SQL)
                row = cur.fetchone()

            if row is None:
                print("No data returned from papers table.")
                return

            (
                total_papers,
                missing_id,
                missing_title,
                negative_citations,
                extreme_citations,
                pub_after_created,
                duplicate_id_groups,
                duplicate_doi_groups,
                missing_primary_topic,
                bad_ai_concept_score,
            ) = row

            print("=== Papers Data Quality Report ===")
            print(f"Total papers: {total_papers}")
            print()
            print("Completeness:")
            print(f"  Missing id: {missing_id}")
            print(f"  Missing title: {missing_title}")
            print(f"  Missing primary_topic_id: {missing_primary_topic}")
            print()
            print("Citations:")
            print(f"  Negative cited_by_count: {negative_citations}")
            print(f"  Extreme cited_by_count (>100000): {extreme_citations}")
            print()
            print("Dates:")
            print(f"  publication_date after created_date: {pub_after_created}")
            print()
            print("Duplicates:")
            print(f"  Duplicate id groups: {duplicate_id_groups}")
            print(f"  Duplicate doi groups: {duplicate_doi_groups}")
            print()
            print("Scores:")
            print(f"  AI concept score out of [0,1] range: {bad_ai_concept_score}")
        finally:
            conn.close()

    def run(self) -> None:
        """
        Run the full pipeline:
        1. Fetch recent AI papers from OpenAlex and save to JSON.
        2. Ensure the database schema exists and load the papers.
        3. Run the data quality report.
        """
        # Step 1: Fetch and save papers from the API
        json_path = self.fetch_and_save_recent_papers()

        # Step 2: Create table(s) if needed and load data
        # (ensure_schema inside load_papers provides full schema creation)
        self.load_papers_into_db(json_path)

        # Step 3: Run data quality summary
        self.run_data_quality_report()


if __name__ == "__main__":
    pipeline = AIPapersPipeline()
    pipeline.run()

