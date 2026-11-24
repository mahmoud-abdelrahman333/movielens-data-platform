-- Business question: Which genres receive the most ratings and have the highest average scores?
-- Each movie rating contributes once to each genre assigned to that movie.
WITH movie_genres AS (
    SELECT
        m.MOVIE_ID,
        f.VALUE::STRING AS genre
    FROM {{ ref('dim_movies') }} AS m,
         LATERAL FLATTEN(INPUT => m.GENRE_ARRAY) AS f
), genre_metrics AS (
    SELECT
        mg.genre,
        COUNT(*) AS rating_count,
        COUNT(DISTINCT r.MOVIE_ID) AS distinct_movies,
        COUNT(DISTINCT r.USER_ID) AS distinct_users,
        ROUND(AVG(r.RATING), 3) AS average_rating
    FROM {{ ref('fct_ratings') }} AS r
    INNER JOIN movie_genres AS mg
        ON r.MOVIE_ID = mg.MOVIE_ID
    GROUP BY mg.genre
)
SELECT
    genre,
    rating_count,
    distinct_movies,
    distinct_users,
    average_rating,
    RANK() OVER (ORDER BY rating_count DESC) AS popularity_rank,
    RANK() OVER (ORDER BY average_rating DESC, rating_count DESC) AS average_rating_rank
FROM genre_metrics
ORDER BY rating_count DESC;
