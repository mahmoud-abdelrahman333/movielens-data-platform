{{config(
    materialized = "table"
)
}}




with raw_ratings as(
    select * from MOVIELENS.RAW.RAW_RATINGS
)


select 
    userid as user_id,
    movieid as movie_id,
    rating,
    TO_TIMESTAMP_LTZ(TIMESTAMP) as rating_timestamp
from raw_ratings