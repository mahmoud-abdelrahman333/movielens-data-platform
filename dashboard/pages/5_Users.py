import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Users | MovieLens", layout="wide")
st.title("User Activity")

summary = run_query("""
WITH per_user AS (
    SELECT USER_ID, COUNT(*) AS RATING_COUNT, AVG(RATING) AS AVG_RATING,
           COUNT(DISTINCT MOVIE_ID) AS DISTINCT_MOVIES
    FROM MOVIELENS.DEV.FCT_RATINGS
    GROUP BY USER_ID
)
SELECT COUNT(*) AS ACTIVE_USERS,
       AVG(RATING_COUNT) AS AVG_RATINGS_PER_USER,
       MEDIAN(RATING_COUNT) AS MEDIAN_RATINGS_PER_USER,
       MAX(RATING_COUNT) AS MAX_RATINGS_BY_USER,
       AVG(AVG_RATING) AS AVG_USER_RATING
FROM per_user
""").iloc[0]

cols = st.columns(3)
cols[0].metric("Active users", f"{int(summary['ACTIVE_USERS']):,}")
cols[1].metric("Average ratings/user", f"{summary['AVG_RATINGS_PER_USER']:.1f}")
cols[2].metric("Median ratings/user", f"{summary['MEDIAN_RATINGS_PER_USER']:.0f}")

activity = run_query("""
SELECT RATING_COUNT, COUNT(*) AS USERS
FROM (
    SELECT USER_ID, COUNT(*) AS RATING_COUNT
    FROM MOVIELENS.DEV.FCT_RATINGS
    GROUP BY USER_ID
)
GROUP BY RATING_COUNT
ORDER BY RATING_COUNT
""")
if not activity.empty:
    fig = px.histogram(activity, x="RATING_COUNT", y="USERS",
                       title="Distribution of user rating activity",
                       nbins=40)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Most active users")
top_users = run_query("""
SELECT USER_ID, COUNT(*) AS RATING_COUNT,
       AVG(RATING) AS AVG_RATING,
       COUNT(DISTINCT MOVIE_ID) AS DISTINCT_MOVIES
FROM MOVIELENS.DEV.FCT_RATINGS
GROUP BY USER_ID
ORDER BY RATING_COUNT DESC
LIMIT 20
""")
st.dataframe(top_users, use_container_width=True, hide_index=True)
