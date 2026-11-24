-- Business question: Which movies are most popular, and which are best rated?
-- A 100-rating minimum is used for the best-rated ranking to reduce tiny-sample bias.
WITH movie_metrics AS (
    SELECT
        m.MOVIE_ID,
        m.MOVIE_TITLE,
        m.GENRES,
        COUNT(*) AS rating_count,
        ROUND(AVG(r.RATING), 3) AS average_rating,
        COUNT(DISTINCT r.USER_ID) AS unique_raters
    FROM {{ ref('fct_ratings') }} AS r
    INNER JOIN {{ ref('dim_movies') }} AS m
        ON r.MOVIE_ID = m.MOVIE_ID
    GROUP BY m.MOVIE_ID, m.MOVIE_TITLE, m.GENRES
)
SELECT
    MOVIE_ID,
    MOVIE_TITLE,
    GENRES,
    rating_count,
    unique_raters,
    average_rating,
    RANK() OVER (ORDER BY rating_count DESC) AS popularity_rank,
    CASE
        WHEN rating_count >= 100
        THEN RANK() OVER (
            PARTITION BY IFF(rating_count >= 100, 1, 0)
            ORDER BY average_rating DESC, rating_count DESC
        )
    END AS qualified_rating_rank
FROM movie_metrics
ORDER BY rating_count DESC;
