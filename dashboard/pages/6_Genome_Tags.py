import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Genome Tags | MovieLens", layout="wide")
st.title("Genome Tag Analysis")

top_n = st.slider("Number of tags to display", min_value=10, max_value=100, value=30, step=10)

tags = run_query(f"""
SELECT t.TAG_ID, t.TAG_NAME,
       COUNT(*) AS MOVIE_COUNT,
       AVG(s.RELEVANCE_SCORE) AS AVG_RELEVANCE,
       MEDIAN(s.RELEVANCE_SCORE) AS MEDIAN_RELEVANCE
FROM MOVIELENS.DEV.FCT_GENOME_SCORES s
JOIN MOVIELENS.DEV.DIM_GENOME_TAGS t
  ON s.TAG_ID = t.TAG_ID
GROUP BY t.TAG_ID, t.TAG_NAME
ORDER BY AVG_RELEVANCE DESC
LIMIT {int(top_n)}
""")

if not tags.empty:
    st.plotly_chart(px.bar(tags.sort_values("AVG_RELEVANCE"),
                           x="AVG_RELEVANCE", y="TAG_NAME", orientation="h",
                           title=f"Top {top_n} tags by average relevance"),
                    use_container_width=True)
    st.dataframe(tags, use_container_width=True, hide_index=True)
else:
    st.info("No genome scores found.")
