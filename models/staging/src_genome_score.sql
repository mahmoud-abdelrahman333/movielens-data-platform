-- Active: 1795475038627@@127.0.0.1@3306@MOVIELENS@RAW
with raw_genome_scores as(
    select * from MOVIELENS.RAW.RAW_GENOME_SCORES
)


select 
    movieid as movie_id,
    tagid as tag_id,
    relevance
from raw_genome_scores