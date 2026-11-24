import streamlit as st
import plotly.express as px
from utils.snowflake_connection import run_query

st.set_page_config(page_title="Movies | MovieLens", layout="wide")
st.title("Movie Performance")

minimum = st.number_input("Minimum number of ratings", min_value=1, value=100, step=50)

movies = run_query(f"""
SELECT m.MOVIE_ID, m.MOVIE_TITLE, m.GENRES,
       COUNT(*) AS RATING_COUNT,
       AVG(r.RATING) AS AVG_RATING
FROM MOVIELENS.DEV.FCT_RATINGS r
JOIN MOVIELENS.DEV.DIM_MOVIES m
  ON r.MOVIE_ID = m.MOVIE_ID
GROUP BY m.MOVIE_ID, m.MOVIE_TITLE, m.GENRES
HAVING COUNT(*) >= {int(minimum)}
ORDER BY AVG_RATING DESC, RATING_COUNT DESC
""")

if not movies.empty:
    left, right = st.columns(2)
    with left:
        st.subheader("Top-rated movies")
        st.dataframe(movies.head(20), use_container_width=True, hide_index=True)
    with right:
        popular = movies.sort_values("RATING_COUNT", ascending=False).head(20)
        st.subheader("Most-rated movies")
        st.plotly_chart(px.bar(popular.sort_values("RATING_COUNT"),
                               x="RATING_COUNT", y="MOVIE_TITLE", orientation="h",
                               title="Top 20 by rating volume"),
                        use_container_width=True)
else:
    st.info("No movies meet this minimum-rating threshold. Try lowering it.")
