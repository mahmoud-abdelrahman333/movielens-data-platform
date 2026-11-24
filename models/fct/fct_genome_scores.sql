with src_scores as(
    select * from {{ ref('src_genome_score') }}
)

SELECT
    movie_id,
    tag_id,
    round(relevance,4) as relevance_score
FROM src_scores 
where relevance > 0