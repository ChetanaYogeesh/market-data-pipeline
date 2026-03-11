import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from database import get_neon_connection


def _short_openalex_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    return url.rstrip("/").rsplit("/", 1)[-1]


def load_works_from_file(path: Path) -> List[Dict[str, Any]]:
    """
    Load works list from a JSON file.

    Supports both:
    - {\"meta\": ..., \"results\": [...]} format
    - Plain list format [...]
    """
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "results" in data:
        results = data["results"]
    else:
        results = data

    if not isinstance(results, list):
        raise RuntimeError(f"Unexpected JSON structure in file: {path}")

    return results


def load_latest_ai_works() -> List[Dict[str, Any]]:
    temp_dir = Path("temp")
    files = sorted(temp_dir.glob("ai_works_*.json"))
    if not files:
        raise RuntimeError("No ai_works_*.json files found in temp/")

    latest = files[-1]
    return load_works_from_file(latest)


def extract_paper_row(work: Dict[str, Any]) -> Tuple:
    work_id = _short_openalex_id(work.get("id"))
    if not work_id:
        raise RuntimeError("Work object missing 'id' field.")

    doi = work.get("doi") or (work.get("ids") or {}).get("doi")
    title = work.get("title") or work.get("display_name") or ""
    abstract = None  # placeholder if you later add plaintext abstracts

    publication_date = work.get("publication_date")
    publication_year = work.get("publication_year")
    created_date = work.get("created_date")
    updated_date = work.get("updated_date")
    wtype = work.get("type")
    language = work.get("language")
    cited_by_count = work.get("cited_by_count")

    citation_percentile = None
    if isinstance(work.get("citation_normalized_percentile"), dict):
        citation_percentile = work["citation_normalized_percentile"].get("value")

    fwci = work.get("fwci")

    open_access = work.get("open_access") or {}
    is_oa = open_access.get("is_oa")
    oa_status = open_access.get("oa_status")
    oa_url = open_access.get("oa_url")

    primary_topic = work.get("primary_topic") or {}
    primary_topic_id = _short_openalex_id(primary_topic.get("id"))
    primary_topic_name = primary_topic.get("display_name")
    primary_domain = (primary_topic.get("domain") or {}).get("display_name")
    primary_field = (primary_topic.get("field") or {}).get("display_name")
    primary_subfield = (primary_topic.get("subfield") or {}).get("display_name")

    ai_concept_score = None
    for concept in work.get("concepts") or []:
        cid = concept.get("id") or ""
        if cid.endswith("/C154945302") or concept.get("display_name") == "Artificial intelligence":
            ai_concept_score = concept.get("score")
            break

    countries_distinct_count = work.get("countries_distinct_count")
    institutions_distinct_count = work.get("institutions_distinct_count")

    has_fulltext = bool(work.get("has_fulltext"))
    is_retracted = work.get("is_retracted")
    is_paratext = work.get("is_paratext")
    relevance_score = work.get("relevance_score")

    return (
        work_id,
        doi,
        title,
        abstract,
        publication_date,
        publication_year,
        created_date,
        updated_date,
        wtype,
        language,
        cited_by_count,
        citation_percentile,
        fwci,
        is_oa,
        oa_status,
        oa_url,
        primary_topic_id,
        primary_topic_name,
        primary_domain,
        primary_field,
        primary_subfield,
        ai_concept_score,
        countries_distinct_count,
        institutions_distinct_count,
        has_fulltext,
        is_retracted,
        is_paratext,
        relevance_score,
    )


def extract_authors(work: Dict[str, Any], paper_id: str) -> List[Tuple]:
    rows: List[Tuple] = []
    for a in work.get("authorships") or []:
        author = a.get("author") or {}
        rows.append(
            (
                paper_id,
                a.get("author_position"),
                a.get("raw_author_name") or author.get("display_name") or "",
                _short_openalex_id(author.get("id")),
                bool(a.get("is_corresponding")),
            )
        )
    return rows


def extract_topics(work: Dict[str, Any], paper_id: str) -> List[Tuple]:
    rows: List[Tuple] = []
    for t in work.get("topics") or []:
        rows.append(
            (
                paper_id,
                _short_openalex_id(t.get("id")),
                t.get("display_name"),
                (t.get("domain") or {}).get("display_name"),
                (t.get("field") or {}).get("display_name"),
                (t.get("subfield") or {}).get("display_name"),
                t.get("score"),
            )
        )
    return rows


def extract_keywords(work: Dict[str, Any], paper_id: str) -> List[Tuple]:
    rows: List[Tuple] = []
    for k in work.get("keywords") or []:
        rows.append(
            (
                paper_id,
                k.get("display_name"),
                k.get("score"),
            )
        )
    return rows


def extract_sdgs(work: Dict[str, Any], paper_id: str) -> List[Tuple]:
    rows: List[Tuple] = []
    for s in work.get("sustainable_development_goals") or []:
        sid = s.get("id")
        short_id = sid.rsplit("/", 1)[-1] if isinstance(sid, str) else None
        rows.append(
            (
                paper_id,
                short_id,
                s.get("display_name"),
            )
        )
    return rows


def ensure_schema(conn) -> None:
    schema_path = Path("schema.sql")
    with schema_path.open(encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def upsert_paper(conn, work: Dict[str, Any]) -> None:
    paper_values = extract_paper_row(work)
    paper_id = paper_values[0]

    with conn.cursor() as cur:
        # Upsert into papers
        cur.execute(
            """
            INSERT INTO papers (
                id, doi, title, abstract, publication_date, publication_year,
                created_date, updated_date, type, language, cited_by_count,
                citation_percentile, fwci, is_oa, oa_status, oa_url,
                primary_topic_id, primary_topic_name, primary_domain,
                primary_field, primary_subfield, ai_concept_score,
                countries_distinct_count, institutions_distinct_count,
                has_fulltext, is_retracted, is_paratext, relevance_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                doi = EXCLUDED.doi,
                title = EXCLUDED.title,
                abstract = EXCLUDED.abstract,
                publication_date = EXCLUDED.publication_date,
                publication_year = EXCLUDED.publication_year,
                created_date = EXCLUDED.created_date,
                updated_date = EXCLUDED.updated_date,
                type = EXCLUDED.type,
                language = EXCLUDED.language,
                cited_by_count = EXCLUDED.cited_by_count,
                citation_percentile = EXCLUDED.citation_percentile,
                fwci = EXCLUDED.fwci,
                is_oa = EXCLUDED.is_oa,
                oa_status = EXCLUDED.oa_status,
                oa_url = EXCLUDED.oa_url,
                primary_topic_id = EXCLUDED.primary_topic_id,
                primary_topic_name = EXCLUDED.primary_topic_name,
                primary_domain = EXCLUDED.primary_domain,
                primary_field = EXCLUDED.primary_field,
                primary_subfield = EXCLUDED.primary_subfield,
                ai_concept_score = EXCLUDED.ai_concept_score,
                countries_distinct_count = EXCLUDED.countries_distinct_count,
                institutions_distinct_count = EXCLUDED.institutions_distinct_count,
                has_fulltext = EXCLUDED.has_fulltext,
                is_retracted = EXCLUDED.is_retracted,
                is_paratext = EXCLUDED.is_paratext,
                relevance_score = EXCLUDED.relevance_score
            """,
            paper_values,
        )

        # Refresh child rows
        cur.execute("DELETE FROM paper_authors WHERE paper_id = %s", (paper_id,))
        cur.execute("DELETE FROM paper_topics WHERE paper_id = %s", (paper_id,))
        cur.execute("DELETE FROM paper_keywords WHERE paper_id = %s", (paper_id,))
        cur.execute("DELETE FROM paper_sdgs WHERE paper_id = %s", (paper_id,))

        author_rows = extract_authors(work, paper_id)
        if author_rows:
            cur.executemany(
                """
                INSERT INTO paper_authors (
                    paper_id, author_position, author_name,
                    author_openalex_id, is_corresponding
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                author_rows,
            )

        topic_rows = extract_topics(work, paper_id)
        if topic_rows:
            cur.executemany(
                """
                INSERT INTO paper_topics (
                    paper_id, topic_id, topic_name,
                    topic_domain, topic_field, topic_subfield, topic_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                topic_rows,
            )

        keyword_rows = extract_keywords(work, paper_id)
        if keyword_rows:
            cur.executemany(
                """
                INSERT INTO paper_keywords (
                    paper_id, keyword, keyword_score
                )
                VALUES (%s, %s, %s)
                """,
                keyword_rows,
            )

        sdg_rows = extract_sdgs(work, paper_id)
        if sdg_rows:
            cur.executemany(
                """
                INSERT INTO paper_sdgs (
                    paper_id, sdg_id, sdg_name
                )
                VALUES (%s, %s, %s)
                """,
                sdg_rows,
            )

    conn.commit()


def main() -> None:
    # If a JSON path is provided as a command-line argument, use it.
    # Otherwise, fall back to the latest ai_works_*.json in temp/.
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
        if not json_path.is_file():
            raise SystemExit(f"JSON file not found: {json_path}")
        works = load_works_from_file(json_path)
        print(f"Loading {len(works)} works from {json_path}...")
    else:
        works = load_latest_ai_works()
        print(f"Loading {len(works)} works from latest file in temp/...")
    conn = get_neon_connection()
    try:
        # Create tables if necessary
        ensure_schema(conn)

        # Insert or update papers and related entities with deduplication
        for i, work in enumerate(works, start=1):
            upsert_paper(conn, work)
            if i % 100 == 0:
                print(f"Upserted {i} papers...")

        print(f"Finished loading {len(works)} papers into the database.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

