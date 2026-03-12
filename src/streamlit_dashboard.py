import streamlit as st
import pandas as pd

from .database import get_neon_connection


@st.cache_data(show_spinner=False)
def load_overview():
    conn = get_neon_connection()
    try:
        overview_sql = """
        SELECT
          COUNT(*) AS total_papers,
          COUNT(*) FILTER (WHERE is_oa = TRUE) AS oa_papers,
          COUNT(*) FILTER (WHERE is_oa = FALSE OR is_oa IS NULL) AS non_oa_papers,
          AVG(cited_by_count) AS avg_citations,
          MAX(cited_by_count) AS max_citations
        FROM papers;
        """
        df = pd.read_sql_query(overview_sql, conn)
    finally:
        conn.close()
    return df.iloc[0]


@st.cache_data(show_spinner=False)
def load_publications_by_date():
    conn = get_neon_connection()
    try:
        sql = """
        SELECT
          publication_date,
          COUNT(*) AS paper_count,
          AVG(cited_by_count) AS avg_citations
        FROM papers
        WHERE publication_date IS NOT NULL
        GROUP BY publication_date
        ORDER BY publication_date;
        """
        df = pd.read_sql_query(sql, conn, parse_dates=["publication_date"])
    finally:
        conn.close()
    return df


@st.cache_data(show_spinner=False)
def load_recent_papers(limit: int = 50, oa_only: bool = False):
    conn = get_neon_connection()
    try:
        base_sql = """
        SELECT
          id,
          title,
          publication_date,
          publication_year,
          cited_by_count,
          is_oa,
          primary_topic_name
        FROM papers
        """
        where_clause = ""
        params = []
        if oa_only:
            where_clause = "WHERE is_oa = TRUE"

        order_limit = " ORDER BY publication_date DESC NULLS LAST, created_date DESC NULLS LAST LIMIT %s"
        params.append(limit)

        sql = base_sql + " " + where_clause + order_limit
        df = pd.read_sql_query(sql, conn, params=params, parse_dates=["publication_date"])
    finally:
        conn.close()
    return df


@st.cache_data(show_spinner=False)
def load_top_topics(limit: int = 10):
    conn = get_neon_connection()
    try:
        sql = """
        SELECT
          primary_topic_name AS topic,
          COUNT(*) AS paper_count,
          AVG(cited_by_count) AS avg_citations
        FROM papers
        WHERE primary_topic_name IS NOT NULL
        GROUP BY primary_topic_name
        ORDER BY paper_count DESC
        LIMIT %s;
        """
        df = pd.read_sql_query(sql, conn, params=(limit,))
    finally:
        conn.close()
    return df


@st.cache_data(show_spinner=False)
def load_citation_distribution():
    conn = get_neon_connection()
    try:
        sql = """
        SELECT cited_by_count
        FROM papers
        WHERE cited_by_count IS NOT NULL;
        """
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df


def main():
    st.set_page_config(
        page_title="AI Papers Dashboard",
        layout="wide",
    )
    st.title("AI Papers Dashboard")
    st.caption(
        "Powered by OpenAlex (PyAlex), Neon PostgreSQL, and Streamlit."
    )

    # Overview metrics
    overview = load_overview()
    total = int(overview["total_papers"] or 0)
    oa = int(overview["oa_papers"] or 0)
    non_oa = int(overview["non_oa_papers"] or 0)
    avg_citations = float(overview["avg_citations"] or 0.0)
    max_citations = int(overview["max_citations"] or 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total papers", f"{total:,}")
    col2.metric("Open access papers", f"{oa:,}")
    col3.metric("Non‑OA / unknown OA", f"{non_oa:,}")
    col4.metric("Avg citations per paper", f"{avg_citations:0.1f}", help=f"Max: {max_citations:,}")

    st.markdown("---")

    # Time series: publications by date
    pubs_df = load_publications_by_date()
    if not pubs_df.empty:
        left, right = st.columns(2)

        with left:
            st.subheader("Papers over time")
            st.line_chart(
                pubs_df.set_index("publication_date")["paper_count"],
                height=300,
            )

        with right:
            st.subheader("Average citations over time")
            st.line_chart(
                pubs_df.set_index("publication_date")["avg_citations"],
                height=300,
            )
    else:
        st.info("No publication date data available yet.")

    st.markdown("---")

    # Top topics
    topic_limit = st.slider("Number of top topics to display", min_value=5, max_value=30, value=10)
    topics_df = load_top_topics(limit=topic_limit)
    st.subheader("Top topics by paper count")
    if not topics_df.empty:
        st.bar_chart(
            topics_df.set_index("topic")["paper_count"],
            height=400,
        )
        with st.expander("Show topic details"):
            st.dataframe(topics_df, use_container_width=True)
    else:
        st.info("No topic data available yet.")

    st.markdown("---")

    # Citation distribution
    st.subheader("Citation distribution")
    citations_df = load_citation_distribution()
    if not citations_df.empty:
        max_cites = int(citations_df["cited_by_count"].max())
        if max_cites <= 0:
            st.info("All papers currently have 0 citations; no distribution to show yet.")
        else:
            # Choose a sensible minimum for the slider
            min_slider = 1
            default_max = min(200, max_cites)
            max_clip = st.slider(
                "Max citations to include in histogram",
                min_value=min_slider,
                max_value=max_cites,
                value=default_max,
            )
            filtered = citations_df[citations_df["cited_by_count"] <= max_clip]
            st.bar_chart(filtered["cited_by_count"].value_counts().sort_index(), height=300)
    else:
        st.info("No citation data available yet.")

    st.markdown("---")

    # Recent papers table
    st.subheader("Recent papers")
    col_left, col_right = st.columns([2, 1])
    with col_right:
        oa_only = st.checkbox("Open access only", value=False)
        table_limit = st.slider(
            "Number of rows to show",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
        )
    with col_left:
        recent_df = load_recent_papers(limit=table_limit, oa_only=oa_only)
        if not recent_df.empty:
            st.dataframe(
                recent_df.rename(
                    columns={
                        "publication_date": "Publication date",
                        "publication_year": "Year",
                        "cited_by_count": "Citations",
                        "is_oa": "Open access",
                        "primary_topic_name": "Primary topic",
                    }
                ),
                use_container_width=True,
            )
        else:
            st.info("No papers loaded into the database yet.")


if __name__ == "__main__":
    main()

