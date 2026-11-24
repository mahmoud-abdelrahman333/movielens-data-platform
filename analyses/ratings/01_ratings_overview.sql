-- Business question: What is the overall scale and coverage of rating activity?
SELECT
    COUNT(*) AS total_ratings,
    COUNT(DISTINCT USER_ID) AS unique_users,
    COUNT(DISTINCT MOVIE_ID) AS unique_movies_rated,
    ROUND(AVG(RATING), 3) AS average_rating,
    MIN(RATING) AS minimum_rating,
    MAX(RATING) AS maximum_rating,
    MIN(RATING_TIMESTAMP) AS first_rating_timestamp,
    MAX(RATING_TIMESTAMP) AS last_rating_timestamp
FROM {{ ref('fct_ratings') }};
