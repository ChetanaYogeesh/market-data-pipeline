-- SQL data quality checks for the papers table

-- 1. Missing Required Data
-- Count rows missing essential identifiers or title
SELECT
    COUNT(*) AS missing_required
FROM papers
WHERE title IS NULL
   OR title = ''
   OR id IS NULL;


-- 2. Citation Anomalies
-- Find papers with clearly invalid citation counts
SELECT
    id,
    title,
    cited_by_count
FROM papers
WHERE cited_by_count < 0
   OR cited_by_count > 100000;


-- 3. Date Logic
-- Publication date should not be after the record created_date
SELECT
    id,
    title,
    publication_date,
    created_date
FROM papers
WHERE publication_date IS NOT NULL
  AND created_date IS NOT NULL
  AND publication_date > created_date;


-- 4. Duplicate Identifiers
-- Detect duplicate IDs or DOIs

-- Duplicate IDs (should never happen because id is the primary key)
SELECT
    id,
    COUNT(*) AS id_count
FROM papers
GROUP BY id
HAVING COUNT(*) > 1;

-- Duplicate DOIs (same DOI used by multiple records)
SELECT
    doi,
    COUNT(*) AS doi_count
FROM papers
WHERE doi IS NOT NULL
GROUP BY doi
HAVING COUNT(*) > 1;


-- 5. Score Range
-- Ensure AI concept score stays within the expected [0, 1] range
SELECT
    id,
    title,
    ai_concept_score
FROM papers
WHERE ai_concept_score IS NOT NULL
  AND (ai_concept_score < 0 OR ai_concept_score > 1);

