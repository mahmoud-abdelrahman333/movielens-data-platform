import streamlit as st
from utils.snowflake_connection import run_query

st.set_page_config(page_title="MovieLens Analytics", page_icon="🎬", layout="wide")

st.title("🎬 MovieLens Analytics")
st.caption("Analytics dashboard powered by Snowflake")

try:
    status = run_query("""
        SELECT CURRENT_DATABASE() AS DATABASE_NAME,
               CURRENT_SCHEMA() AS SCHEMA_NAME,
               CURRENT_WAREHOUSE() AS WAREHOUSE_NAME
    """)
    row = status.iloc[0]
    st.success(
        f"Connected to {row['DATABASE_NAME']}.{row['SCHEMA_NAME']} "
        f"using warehouse {row['WAREHOUSE_NAME']}."
    )
except Exception as exc:
    st.error("Could not connect to Snowflake. Check your .streamlit/secrets.toml settings.")
    st.exception(exc)
    st.stop()

st.markdown("""
### Dashboard sections
Use the pages in the sidebar to explore:

- **Overview:** headline KPIs and rating activity over time.
- **Ratings:** rating distribution and trends.
- **Movies:** most-rated and highest-rated movies.
- **Genres:** rating activity and average rating by genre.
- **Users:** user activity and rating behavior.
- **Genome Tags:** tag relevance across movies.

All pages query the existing `MOVIELENS.DEV` warehouse tables directly.
""")

if st.button("Refresh cached data"):
    st.cache_data.clear()
    st.rerun()
