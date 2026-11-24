-- Business question: How does rating activity and average score change over time?
SELECT
    DATE_TRUNC('MONTH', RATING_TIMESTAMP)::DATE AS rating_month,
    COUNT(*) AS total_ratings,
    COUNT(DISTINCT USER_ID) AS active_users,
    COUNT(DISTINCT MOVIE_ID) AS movies_rated,
    ROUND(AVG(RATING), 3) AS average_rating
FROM {{ ref('fct_ratings') }}
WHERE RATING_TIMESTAMP IS NOT NULL
GROUP BY 1
ORDER BY 1;
