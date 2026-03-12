-- Core papers table with simplified, dashboard-friendly fields
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,                          -- OpenAlex work ID (short form)
    doi TEXT,
    title TEXT NOT NULL,
    abstract TEXT,
    publication_date DATE,
    publication_year INTEGER,
    created_date TIMESTAMPTZ,
    updated_date TIMESTAMPTZ,
    type TEXT,
    language TEXT,
    cited_by_count INTEGER,
    citation_percentile NUMERIC,
    fwci NUMERIC,
    is_oa BOOLEAN,
    oa_status TEXT,
    oa_url TEXT,
    primary_topic_id TEXT,
    primary_topic_name TEXT,
    primary_domain TEXT,
    primary_field TEXT,
    primary_subfield TEXT,
    ai_concept_score NUMERIC,
    countries_distinct_count INTEGER,
    institutions_distinct_count INTEGER,
    has_fulltext BOOLEAN,
    is_retracted BOOLEAN,
    is_paratext BOOLEAN,
    relevance_score NUMERIC
);

-- Authors associated with a paper
CREATE TABLE IF NOT EXISTS paper_authors (
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    author_position TEXT,
    author_name TEXT NOT NULL,
    author_openalex_id TEXT,
    is_corresponding BOOLEAN
);

-- Topics associated with a paper
CREATE TABLE IF NOT EXISTS paper_topics (
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    topic_id TEXT,
    topic_name TEXT,
    topic_domain TEXT,
    topic_field TEXT,
    topic_subfield TEXT,
    topic_score NUMERIC
);

-- Keywords (lightweight tags) associated with a paper
CREATE TABLE IF NOT EXISTS paper_keywords (
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    keyword TEXT,
    keyword_score NUMERIC
);

-- Sustainable Development Goals associated with a paper
CREATE TABLE IF NOT EXISTS paper_sdgs (
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers (id) ON DELETE CASCADE,
    sdg_id TEXT,
    sdg_name TEXT
);

