import json 
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pyalex
from pyalex import Concepts, Works


def get_ai_concept_id() -> str:
    concepts = Concepts().search("Artificial Intelligence").get(per_page=1)
    if not concepts:
        raise RuntimeError("Could not find 'Artificial Intelligence' concept in OpenAlex.")

    concept = concepts[0]
    concept_id = concept.get("id")
    if not concept_id:
        raise RuntimeError("Concept result does not contain an 'id' field.")

    # Use the short ID form (e.g. C41008148) for filtering
    if concept_id.startswith("https://openalex.org/"):
        concept_id = concept_id.rsplit("/", 1)[-1]

    return concept_id


def fetch_recent_ai_works(
    concept_id: str,
    days: int = 3,
    title_search: str | None = "artificial intelligence",
) -> tuple[list[dict], dict]:
    today = date.today()
    start_date = today - timedelta(days=days)

    query = Works()

    # Use OpenAlex's search_filter on the title field to avoid
    # downloading obviously irrelevant papers.
    if title_search:
        query = query.search_filter(title=title_search)

    query = (
        query.filter(concepts={"id": concept_id})
        .filter(from_publication_date=start_date.isoformat())
        .filter(to_publication_date=today.isoformat())
        .filter(type="article")
    )

    works: list[dict] = []
    for page in query.paginate(per_page=200, n_max=None):
        works.extend(page)

    # Ask OpenAlex how many records match this query
    expected_count = query.count()

    meta = {
        "concept_id": concept_id,
        "from_publication_date": start_date.isoformat(),
        "to_publication_date": today.isoformat(),
        "expected_count": expected_count,
        "fetched_count": len(works),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    # Safety check: log if we did not retrieve all expected records
    if expected_count is not None and len(works) != expected_count:
        print(
            f"Warning: expected {expected_count} works from OpenAlex "
            f"but fetched {len(works)} records."
        )

    return works, meta


def save_works_to_timestamped_file(works: list[dict], meta: dict) -> Path:
    output_dir = Path("temp")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"ai_works_{timestamp}.json"

    payload = {
        "meta": meta,
        "results": works,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return output_path


def main() -> None:
    api_key = os.getenv("OPENALEX_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Please set the OPENALEX_API_KEY environment variable before running this script."
        )

    pyalex.config.api_key = api_key

    concept_id = get_ai_concept_id()
    works, meta = fetch_recent_ai_works(concept_id, days=3)
    output_path = save_works_to_timestamped_file(works, meta)

    print(
        f"Saved {len(works)} AI works from the last 3 days to {output_path} "
        f"(expected_count={meta['expected_count']})"
    )


if __name__ == "__main__":
    main()

