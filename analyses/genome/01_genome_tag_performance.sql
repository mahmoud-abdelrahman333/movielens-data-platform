-- Business question: Which genome tags are most strongly associated with movies overall?
SELECT
    t.TAG_ID,
    t.TAG_NAME,
    COUNT(*) AS movie_tag_pairs,
    COUNT(DISTINCT s.MOVIE_ID) AS distinct_movies,
    ROUND(AVG(s.RELEVANCE_SCORE), 4) AS average_relevance,
    ROUND(MIN(s.RELEVANCE_SCORE), 4) AS minimum_relevance,
    ROUND(MAX(s.RELEVANCE_SCORE), 4) AS maximum_relevance
FROM {{ ref('fct_genome_scores') }} AS s
INNER JOIN {{ ref('dim_genome_tags') }} AS t
    ON s.TAG_ID = t.TAG_ID
GROUP BY t.TAG_ID, t.TAG_NAME
ORDER BY average_relevance DESC, movie_tag_pairs DESC;
