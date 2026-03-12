## Error Log and Resolutions

This file summarizes the main errors encountered during development and how they were handled.

---

### 1. Missing `OPENALEX_API_KEY`

- **Error**
  - `RuntimeError: Please set the OPENALEX_API_KEY environment variable before running this script.`
- **Context**
  - Running `list_ai_papers.py` and `fetch_recent_ai_papers.py` before configuring the OpenAlex API key.
- **Resolution**
  - Documented the need for an OpenAlex API key and how to obtain it.
  - Instructed to set `OPENALEX_API_KEY` as an environment variable (e.g. via `.env` or `export` in the shell) before running scripts.

---

### 2. Git divergence between `main` and `origin/main`

- **Error**
  - `git status` reported: `main...origin/main [ahead 1, behind 1]`.
- **Context**
  - Local `main` contained a new commit, while `origin/main` had a different new commit.
- **Resolution**
  - Explained that the branches had diverged and recommended reconciling via:
    - `git fetch origin`
    - `git rebase origin/main` (or merge) followed by `git push origin main`.

---

### 3. Psycopg2 module missing

- **Error**
  - `ModuleNotFoundError: No module named 'psycopg2'`
- **Context**
  - Importing `psycopg2` in `database.py` before the dependency was installed.
- **Resolution**
  - Installed `psycopg2-binary` in the virtual environment:
    - `pip install psycopg2-binary`
  - Added `psycopg2-binary` to `requirements.txt`.

---

### 4. `pkg_resources` missing when installing `pandas`

- **Error**
  - `ModuleNotFoundError: No module named 'pkg_resources'` during `pip install -r requirements.txt`.
- **Context**
  - Building `pandas==2.0.3` from source in the `venv` without `setuptools` installed.
- **Resolution**
  - Installed `setuptools` and `wheel` into the virtual environment:
    - `pip install setuptools wheel`
  - After that, `psycopg2-binary` and other dependencies installed cleanly.

---

### 5. Missing `dotenv` module

- **Error**
  - `ModuleNotFoundError: No module named 'dotenv'`
- **Context**
  - Importing `from dotenv import load_dotenv` in `database.py` to read `.env` variables.
- **Resolution**
  - Installed `python-dotenv` in the virtual environment and added it to `requirements.txt`.

---

### 6. JSON loader f-string syntax error

- **Error**
  - `SyntaxError: unexpected character after line continuation character` at:
    - `raise RuntimeError(f\"Unexpected JSON structure in file: {path}\")`
- **Context**
  - In `load_papers.py`, an f-string contained escaped quotes that were unnecessary in the actual Python file.
- **Resolution**
  - Replaced the line with a correct f-string:
    - `raise RuntimeError(f"Unexpected JSON structure in file: {path}")`

---

### 7. Running SQL as Python (comment syntax errors)

- **Errors**
  - `SyntaxError: unterminated string literal (detected at line ...)`
  - `SyntaxError: invalid syntax` pointing at lines beginning with `--` in `tests_papers.sql`.
- **Context**
  - Attempting to run the SQL test file as Python code, where `--` comments and embedded apostrophes/backticks were misinterpreted.
- **Resolution**
  - Clarified that `.sql` files must be executed with Postgres tools like `psql` rather than Python.
  - Simplified comments in `tests_papers.sql` to avoid problematic characters when the file is embedded in Python strings.
  - Where embedded in Python (e.g. `run_data_quality.py`), used `textwrap.dedent` and plain comments inside the SQL string.

---

### 8. Title-based duplicate detection changed to IDs/DOIs

- **Issue**
  - Initial design of data quality tests checked for duplicate titles, which can be legitimate (different papers sharing similar titles).
- **Context**
  - User requested that duplicates be detected only on IDs and DOIs.
- **Resolution**
  - Updated `tests_papers.sql` to:
    - Check duplicate `id` values.
    - Check duplicate `doi` values.
  - Updated `run_data_quality.py` to report `duplicate_id_groups` and `duplicate_doi_groups` instead of duplicate titles.

---

### 9. Neon database connectivity in sandbox

- **Error**
  - `psycopg2.OperationalError: could not translate host name ... to address`
- **Context**
  - Attempting to connect to the Neon database from the sandboxed environment, which cannot resolve or reach the Neon host.
- **Resolution**
  - Not a code bug; documented that:
    - The connection helper works, but must be run locally (outside the sandbox) where the Neon host is reachable.
    - Provided the exact command for the user to run locally:
      - `python -c "from database import create_papers_table; create_papers_table()"`.

