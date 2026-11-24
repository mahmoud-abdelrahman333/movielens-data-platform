-- Business question: Are there nulls, duplicate business keys, or orphan dimension keys?
-- Each row is one check. A non-zero issue_count should be investigated.
WITH checks AS (
    SELECT 'FCT_RATINGS: null USER_ID' AS check_name, COUNT_IF(USER_ID IS NULL) AS issue_count
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT 'FCT_RATINGS: null MOVIE_ID', COUNT_IF(MOVIE_ID IS NULL)
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT 'FCT_RATINGS: null RATING', COUNT_IF(RATING IS NULL)
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT 'FCT_RATINGS: null RATING_TIMESTAMP', COUNT_IF(RATING_TIMESTAMP IS NULL)
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT 'FCT_RATINGS: ratings outside 0.5-5', COUNT_IF(RATING < 0.5 OR RATING > 5)
    FROM {{ ref('fct_ratings') }}
    UNION ALL
    SELECT 'FCT_RATINGS: orphan MOVIE_ID', COUNT_IF(m.MOVIE_ID IS NULL)
    FROM {{ ref('fct_ratings') }} AS r
    LEFT JOIN {{ ref('dim_movies') }} AS m ON r.MOVIE_ID = m.MOVIE_ID
    WHERE r.MOVIE_ID IS NOT NULL
    UNION ALL
    SELECT 'FCT_RATINGS: orphan USER_ID', COUNT_IF(u.USER_ID IS NULL)
    FROM {{ ref('fct_ratings') }} AS r
    LEFT JOIN {{ ref('dim_users') }} AS u ON r.USER_ID = u.USER_ID
    WHERE r.USER_ID IS NOT NULL
    UNION ALL
    SELECT 'DIM_MOVIES: duplicate MOVIE_ID', COUNT(*)
    FROM (
        SELECT MOVIE_ID
        FROM {{ ref('dim_movies') }}
        GROUP BY MOVIE_ID
        HAVING COUNT(*) > 1
    )
    UNION ALL
    SELECT 'DIM_USERS: duplicate USER_ID', COUNT(*)
    FROM (
        SELECT USER_ID
        FROM {{ ref('dim_users') }}
        GROUP BY USER_ID
        HAVING COUNT(*) > 1
    )
    UNION ALL
    SELECT 'FCT_GENOME_SCORES: orphan MOVIE_ID', COUNT_IF(m.MOVIE_ID IS NULL)
    FROM {{ ref('fct_genome_scores') }} AS s
    LEFT JOIN {{ ref('dim_movies') }} AS m ON s.MOVIE_ID = m.MOVIE_ID
    WHERE s.MOVIE_ID IS NOT NULL
    UNION ALL
    SELECT 'FCT_GENOME_SCORES: orphan TAG_ID', COUNT_IF(t.TAG_ID IS NULL)
    FROM {{ ref('fct_genome_scores') }} AS s
    LEFT JOIN {{ ref('dim_genome_tags') }} AS t ON s.TAG_ID = t.TAG_ID
    WHERE s.TAG_ID IS NOT NULL
)
SELECT check_name, issue_count
FROM checks
ORDER BY check_name;
