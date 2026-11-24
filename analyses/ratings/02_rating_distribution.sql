-- Business question: How are ratings distributed across the 0.5-5 scale?
SELECT
    RATING,
    COUNT(*) AS rating_count,
    ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS rating_percentage
FROM {{ ref('fct_ratings') }}
GROUP BY RATING
ORDER BY RATING;
