from textwrap import dedent

from .database import get_neon_connection


SUMMARY_SQL = dedent(
    """
    SELECT
      COUNT(*) AS total_papers,

      -- Missing required fields
      COUNT(*) FILTER (WHERE id IS NULL) AS missing_id,
      COUNT(*) FILTER (WHERE title IS NULL OR title = '') AS missing_title,

      -- Citation anomalies
      COUNT(*) FILTER (WHERE cited_by_count < 0) AS negative_citations,
      COUNT(*) FILTER (WHERE cited_by_count > 100000) AS extreme_citations,

      -- Date inconsistencies
      COUNT(*) FILTER (
        WHERE publication_date IS NOT NULL
          AND created_date IS NOT NULL
          AND publication_date > created_date
      ) AS pub_after_created,

      -- Duplicate identifiers
      (
        SELECT COUNT(*) FROM (
          SELECT id
          FROM papers
          GROUP BY id
          HAVING COUNT(*) > 1
        ) AS dup_ids
      ) AS duplicate_id_groups,

      (
        SELECT COUNT(*) FROM (
          SELECT doi
          FROM papers
          WHERE doi IS NOT NULL
          GROUP BY doi
          HAVING COUNT(*) > 1
        ) AS dup_dois
      ) AS duplicate_doi_groups,

      -- Topic coverage
      COUNT(*) FILTER (WHERE primary_topic_id IS NULL) AS missing_primary_topic,

      -- AI concept score range check
      COUNT(*) FILTER (
        WHERE ai_concept_score IS NOT NULL
          AND (ai_concept_score < 0 OR ai_concept_score > 1)
      ) AS bad_ai_concept_score
    FROM papers;
    """
)


def main() -> None:
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


if __name__ == "__main__":
    main()

