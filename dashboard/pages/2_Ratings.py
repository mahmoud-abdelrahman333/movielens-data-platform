import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Ratings | MovieLens", layout="wide")
st.title("Ratings Analysis")

dist = run_query("""
SELECT RATING, COUNT(*) AS RATING_COUNT
FROM MOVIELENS.DEV.FCT_RATINGS
GROUP BY RATING
ORDER BY RATING
""")
if not dist.empty:
    fig = px.bar(dist, x="RATING", y="RATING_COUNT",
                 title="Rating distribution", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

trend = run_query("""
SELECT DATE_TRUNC('MONTH', RATING_TIMESTAMP)::DATE AS RATING_MONTH,
       COUNT(*) AS RATING_COUNT,
       AVG(RATING) AS AVG_RATING
FROM MOVIELENS.DEV.FCT_RATINGS
GROUP BY 1
ORDER BY 1
""")
if not trend.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(trend, x="RATING_MONTH", y="RATING_COUNT",
                                title="Rating volume by month", markers=True),
                        use_container_width=True)
    with col2:
        st.plotly_chart(px.line(trend, x="RATING_MONTH", y="AVG_RATING",
                                title="Average rating by month", markers=True),
                        use_container_width=True)

st.subheader("Rating summary")
summary = run_query("""
SELECT COUNT(*) AS TOTAL_RATINGS,
       MIN(RATING) AS MIN_RATING,
       MAX(RATING) AS MAX_RATING,
       AVG(RATING) AS AVG_RATING,
       MEDIAN(RATING) AS MEDIAN_RATING,
       STDDEV(RATING) AS STDDEV_RATING
FROM MOVIELENS.DEV.FCT_RATINGS
""")
st.dataframe(summary, use_container_width=True, hide_index=True)
