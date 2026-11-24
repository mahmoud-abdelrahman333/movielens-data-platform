-- Business question: How active are users, and how do their rating habits differ?
SELECT
    u.USER_ID,
    COUNT(*) AS ratings_submitted,
    COUNT(DISTINCT r.MOVIE_ID) AS distinct_movies_rated,
    ROUND(AVG(r.RATING), 3) AS average_rating_given,
    MIN(r.RATING) AS lowest_rating_given,
    MAX(r.RATING) AS highest_rating_given,
    MIN(r.RATING_TIMESTAMP) AS first_rating_timestamp,
    MAX(r.RATING_TIMESTAMP) AS last_rating_timestamp
FROM {{ ref('fct_ratings') }} AS r
INNER JOIN {{ ref('dim_users') }} AS u
    ON r.USER_ID = u.USER_ID
GROUP BY u.USER_ID
ORDER BY ratings_submitted DESC;
