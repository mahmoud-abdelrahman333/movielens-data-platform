-- Business question: What are the strongest genome tags associated with each movie?
-- Returns the top 5 tags per movie by relevance score.
WITH ranked_tags AS (
    SELECT
        m.MOVIE_ID,
        m.MOVIE_TITLE,
        t.TAG_NAME,
        s.RELEVANCE_SCORE,
        ROW_NUMBER() OVER (
            PARTITION BY m.MOVIE_ID
            ORDER BY s.RELEVANCE_SCORE DESC, t.TAG_NAME
        ) AS tag_rank
    FROM {{ ref('fct_genome_scores') }} AS s
    INNER JOIN {{ ref('dim_movies') }} AS m
        ON s.MOVIE_ID = m.MOVIE_ID
    INNER JOIN {{ ref('dim_genome_tags') }} AS t
        ON s.TAG_ID = t.TAG_ID
)
SELECT
    MOVIE_ID,
    MOVIE_TITLE,
    TAG_NAME,
    RELEVANCE_SCORE,
    tag_rank
FROM ranked_tags
WHERE tag_rank <= 5
ORDER BY MOVIE_ID, tag_rank;
