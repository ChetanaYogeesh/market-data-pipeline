## Chat Prompts Log

This file summarizes the key prompts and tasks from the Cursor chat session that built this project.

1. **Environment & dependencies**
   - Install the latest `streamlit` into the project `venv` and pin it in `requirements.txt`.
   - Add `pyalex==0.18` to the current `venv` and track it in `requirements.txt`.

2. **Quick PyAlex script**
   - Write a temporary script that uses `pyalex` to display the titles of 5 AI papers.
   - Run the script (which required setting `OPENALEX_API_KEY`).
   - Instructions to obtain a free OpenAlex API key and configure it via environment variables.

3. **Recent AI papers extraction**
   - Task: Write a script that uses the OpenAlex API to find recent AI research papers.
   - Steps:
     1. Search OpenAlex Concepts for "Artificial Intelligence".
     2. Get the concept ID from the search results.
     3. Use that concept ID to filter works from the last 3 days.
     4. Save all papers (with all fields) in a timestamped JSON file inside a `temp/` folder (gitignored).
   - Follow-up prompts:
     - Investigate why only ~25 papers were returned and fix the issue.
     - Add metadata into the JSON file (query parameters, counts, timestamps).
     - Find ways to filter directly on the API to avoid downloading irrelevant papers (title search, type filter).

4. **Git & README**
   - Review and "fix" git commit messages (clarify that existing messages on `origin/main` should not be rewritten, but improve future commit templates).
   - Diagnose a git sync issue where `main` was both ahead and behind `origin/main`.
   - Format provided architecture and tooling guidance into the project `README.md`.

5. **Neon PostgreSQL connection**
   - Use the given Neon connection string and load the password from a `DB_PASSWORD` variable in `.env`.
   - Implement connection handling in `database.py` with `get_neon_connection()`.
   - Create a helper to create the simplified `papers` table if it does not exist.

6. **Simplified schema design**
   - Using a sample paper object from the JSON file, propose a simplified, unnested schema for a Postgres `papers` table and related tables, focused on:
     - Quantitative measures for citations and scores.
     - Essential categorical fields (topics, domains, SDGs, etc.).
   - Implement the schema in SQL and create a script to load data into it.

7. **Extraction and loading**
   - Create an extraction script that:
     - Accepts a JSON filepath like those in `temp/`.
     - Loads the data from JSON.
     - Connects to the database using `database.py`.
     - Creates the `papers` table (and related tables) if necessary.
     - Inserts or updates data with deduplication based on paper ID and refreshes child tables.

8. **Data quality tests**
   - Suggest essential data tests that can be run directly on the `papers` table as SQL queries:
     - Missing required data.
     - Citation anomalies.
     - Date logic checks.
     - Duplicate identifiers (IDs and DOIs).
     - Score ranges for concept scores.
   - Implement these tests in a SQL test file.
   - Build a Python-based data quality report runner and document it in the README.

9. **README enhancements**
   - Add sections describing:
     - Vibe Coding setup checklist (GitHub, Streamlit, Cursor, Neon).
     - Version control best practices.
     - Virtual environments and `requirements.txt`.
     - Working with Cursor in Agent mode.
     - Overall pipeline architecture.
     - Data quality report for the `papers` table and how to run it.

