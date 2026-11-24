import streamlit as st
import pandas as pd

from utils.snowflake_connection import get_connection


st.set_page_config(
    page_title="Movie Recommendations",
    page_icon="🎬",
    layout="wide"
)

st.title("Movie Recommendations")
st.write("Discover movies recommended for you based on your rating history.")

st.divider()


@st.cache_data(ttl=300)
def get_recommendations(user_id):

    connection = get_connection()

    query = """
        SELECT
            R.USER_ID,
            R.MOVIE_ID,
            M.MOVIE_TITLE,
            M.GENRES,
            R.PREDICTED_RATING,
            R.RECOMMENDATION_RANK
        FROM MOVIELENS.DEV.ML_MOVIE_RECOMMENDATIONS R
        LEFT JOIN MOVIELENS.DEV.DIM_MOVIES M
            ON R.MOVIE_ID = M.MOVIE_ID
        WHERE R.USER_ID = %s
        ORDER BY R.RECOMMENDATION_RANK
        LIMIT 10
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query, (user_id,))
        results = cursor.fetch_pandas_all()
        cursor.close()
        return results

    finally:
        connection.close()


# User input
st.subheader("Find Your Recommendations")

col1, col2 = st.columns([3, 1])

with col1:
    user_id = st.number_input(
        "Enter your User ID",
        min_value=1,
        step=1,
        value=1
    )

with col2:
    st.write("")
    st.write("")
    search = st.button("Get Recommendations", use_container_width=True)


if search:

    with st.spinner("Finding your recommended movies..."):

        recommendations = get_recommendations(int(user_id))

    if recommendations.empty:

        st.warning(
            "No recommendations found for this User ID. "
            "Please check the ID and try again."
        )

    else:

        st.success(
            f"Found {len(recommendations)} recommendations for User {user_id}."
        )

        st.divider()

        st.subheader("Your Top 10 Movies")

        for _, movie in recommendations.iterrows():

            rank = int(movie["RECOMMENDATION_RANK"])
            title = movie["MOVIE_TITLE"]
            genres = movie["GENRES"]
            predicted_rating = float(movie["PREDICTED_RATING"])

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### #{rank}  {title}")
                    st.caption(f"Genres: {genres if pd.notna(genres) else 'Unknown'}")

                with col2:
                    st.metric(
                        "Predicted Rating",
                        f"{predicted_rating:.2f} / 5"
                    )