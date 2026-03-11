Here’s what `fetch_recent_ai_papers.py` does, step by step:

- **Resolve the AI concept**  
  - Calls `get_ai_concept_id()` which:
    - Uses `Concepts().search("Artificial Intelligence").get(per_page=1)` to find the AI concept in OpenAlex.
    - Extracts its `id` and normalizes it to the short form (e.g. `C41008148`).

- **Query recent AI works from OpenAlex**  
  - `fetch_recent_ai_works(...)`:
    - Computes a date range: today and `today - 3 days`.
    - Builds a `Works()` query with:
      - `search_filter(title="artificial intelligence")` (title contains this term).
      - `.filter(concepts={"id": concept_id})` (tagged with the AI concept).
      - `.filter(from_publication_date=...)` and `.filter(to_publication_date=...)` (last 3 days).
      - `.filter(type="article")` (only articles).
    - Uses `paginate(per_page=200, n_max=None)` to fetch **all matching works** page by page.
    - Calls `query.count()` to get `expected_count` from OpenAlex.
    - Builds a `meta` dict with:
      - Concept ID
      - Date range
      - `expected_count` vs `fetched_count`
      - `generated_at` timestamp (UTC, ISO8601).
    - Returns `(works, meta)`.

- **Write timestamped JSON output**  
  - `save_works_to_timestamped_file(works, meta)`:
    - Ensures `temp/` exists.
    - Creates a filename like `temp/ai_works_YYYYMMDD_HHMMSS.json`.
    - Writes a JSON object:
      - `"meta": {...}` (metadata above).
      - `"results": [...]` (list of all work dicts).

- **Script entry point / API key handling**  
  - `main()`:
    - Reads `OPENALEX_API_KEY` from the environment; fails with a clear error if missing.
    - Configures `pyalex.config.api_key`.
    - Calls `get_ai_concept_id()`, `fetch_recent_ai_works(...)`, and `save_works_to_timestamped_file(...)`.
    - Prints a summary line with how many works were saved and the `expected_count`.
