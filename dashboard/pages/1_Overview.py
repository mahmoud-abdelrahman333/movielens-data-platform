import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Overview | MovieLens", layout="wide")
st.title("Overview")

kpis = run_query("""
WITH rating_stats AS (
    SELECT COUNT(*) AS TOTAL_RATINGS,
           COUNT(DISTINCT USER_ID) AS ACTIVE_USERS,
           COUNT(DISTINCT MOVIE_ID) AS RATED_MOVIES,
           AVG(RATING) AS AVG_RATING
    FROM MOVIELENS.DEV.FCT_RATINGS
),
movie_stats AS (
    SELECT COUNT(*) AS TOTAL_MOVIES
    FROM MOVIELENS.DEV.DIM_MOVIES
),
user_stats AS (
    SELECT COUNT(*) AS TOTAL_USERS
    FROM MOVIELENS.DEV.DIM_USERS
)
SELECT r.TOTAL_RATINGS, r.ACTIVE_USERS, r.RATED_MOVIES,
       r.AVG_RATING, m.TOTAL_MOVIES, u.TOTAL_USERS
FROM rating_stats r
CROSS JOIN movie_stats m
CROSS JOIN user_stats u
""").iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Total ratings", f"{int(kpis['TOTAL_RATINGS']):,}")
c2.metric("Registered users", f"{int(kpis['TOTAL_USERS']):,}")
c3.metric("Movies in dimension", f"{int(kpis['TOTAL_MOVIES']):,}")
c4, c5, c6 = st.columns(3)
c4.metric("Active users", f"{int(kpis['ACTIVE_USERS']):,}")
c5.metric("Movies rated", f"{int(kpis['RATED_MOVIES']):,}")
c6.metric("Average rating", f"{kpis['AVG_RATING']:.2f}/5" if kpis["AVG_RATING"] is not None else "—")

st.subheader("Rating activity over time")
trend = run_query("""
SELECT DATE_TRUNC('MONTH', RATING_TIMESTAMP)::DATE AS RATING_MONTH,
       COUNT(*) AS RATING_COUNT,
       AVG(RATING) AS AVG_RATING
FROM MOVIELENS.DEV.FCT_RATINGS
GROUP BY 1
ORDER BY 1
""")
if not trend.empty:
    fig = px.line(trend, x="RATING_MONTH", y="RATING_COUNT",
                  title="Number of ratings per month", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No rating records found.")
