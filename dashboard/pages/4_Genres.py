import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Genres | MovieLens", layout="wide")
st.title("Genre Analysis")
st.caption("Each movie rating is attributed to every genre assigned to that movie.")

genres = run_query("""
WITH movie_genres AS (
    SELECT m.MOVIE_ID, f.VALUE::STRING AS GENRE
    FROM MOVIELENS.DEV.DIM_MOVIES m,
         LATERAL FLATTEN(INPUT => m.GENRE_ARRAY) f
)
SELECT g.GENRE,
       COUNT(*) AS RATING_COUNT,
       COUNT(DISTINCT r.USER_ID) AS UNIQUE_USERS,
       COUNT(DISTINCT r.MOVIE_ID) AS MOVIES_RATED,
       AVG(r.RATING) AS AVG_RATING
FROM movie_genres g
JOIN MOVIELENS.DEV.FCT_RATINGS r
  ON g.MOVIE_ID = r.MOVIE_ID
GROUP BY g.GENRE
ORDER BY RATING_COUNT DESC
""")

if not genres.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(genres, x="GENRE", y="RATING_COUNT",
                               title="Rating volume by genre"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(genres.sort_values("AVG_RATING", ascending=False),
                               x="GENRE", y="AVG_RATING",
                               title="Average rating by genre"),
                        use_container_width=True)
    st.dataframe(genres, use_container_width=True, hide_index=True)
else:
    st.info("No genre/rating records found. Check the values stored in GENRE_ARRAY.")
