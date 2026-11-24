import tomllib
from pathlib import Path

import pandas as pd
import snowflake.connector

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, row_number
from pyspark.sql.window import Window
from pyspark.ml.recommendation import ALSModel


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(__file__).resolve().parent / "als_model"

TABLE_NAME = "MOVIELENS.DEV.ML_MOVIE_RECOMMENDATIONS"

TOP_CANDIDATES = 50
TOP_RECOMMENDATIONS = 10
BATCH_SIZE = 5000


# --------------------------------------------------
# Snowflake Connection
# --------------------------------------------------

def get_snowflake_connection():

    secrets_path = (
        PROJECT_DIR
        / "dashboard"
        / ".streamlit"
        / "secrets.toml"
    )

    with open(secrets_path, "rb") as file:
        config = tomllib.load(file)["snowflake"]

    return snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        warehouse=config["warehouse"],
        database=config["database"],
        schema=config["schema"],
        role=config["role"],
    )


# --------------------------------------------------
# Load Previously Rated Movies
# --------------------------------------------------

def load_rated_movies(spark):

    connection = get_snowflake_connection()

    query = """
        SELECT DISTINCT
            USER_ID,
            MOVIE_ID
        FROM MOVIELENS.DEV.FCT_RATINGS
        WHERE USER_ID IS NOT NULL
          AND MOVIE_ID IS NOT NULL
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query)

        ratings_pdf = cursor.fetch_pandas_all()

    finally:
        connection.close()

    return spark.createDataFrame(ratings_pdf).select(
        col("USER_ID").cast("int"),
        col("MOVIE_ID").cast("int"),
    )


# --------------------------------------------------
# Create Recommendations Table
# --------------------------------------------------

def prepare_snowflake_table(connection):

    cursor = connection.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            USER_ID NUMBER(10, 0),
            MOVIE_ID NUMBER(10, 0),
            PREDICTED_RATING FLOAT,
            RECOMMENDATION_RANK NUMBER(10, 0),
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)

    cursor.execute(f"TRUNCATE TABLE {TABLE_NAME}")

    cursor.close()


# --------------------------------------------------
# Save Recommendations in Batches
# --------------------------------------------------

def save_recommendations(recommendations):

    connection = get_snowflake_connection()

    insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            USER_ID,
            MOVIE_ID,
            PREDICTED_RATING,
            RECOMMENDATION_RANK
        )
        VALUES (%s, %s, %s, %s)
    """

    try:
        prepare_snowflake_table(connection)

        cursor = connection.cursor()
        batch = []
        total_inserted = 0

        for row in recommendations.toLocalIterator():

            batch.append((
                int(row["USER_ID"]),
                int(row["MOVIE_ID"]),
                float(row["PREDICTED_RATING"]),
                int(row["RECOMMENDATION_RANK"]),
            ))

            if len(batch) >= BATCH_SIZE:

                cursor.executemany(insert_query, batch)
                total_inserted += len(batch)

                print(f"Inserted {total_inserted:,} recommendations")

                batch.clear()

        if batch:
            cursor.executemany(insert_query, batch)
            total_inserted += len(batch)

        connection.commit()

        print(f"\nTotal recommendations inserted: {total_inserted:,}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    spark = (
        SparkSession.builder
        .appName("MovieLens-ALS-Recommendations")
        .master("local[4]")
        .config("spark.driver.memory", "5g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.default.parallelism", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:

        # Load trained model
        print("\nLoading ALS model...")

        model = ALSModel.load(str(MODEL_PATH))

        print("Model loaded successfully!")

        # Load rated movies
        print("\nLoading previously rated movies...")

        rated_movies = load_rated_movies(spark)

        # Generate candidate recommendations
        print("\nGenerating candidate recommendations...")

        candidates = model.recommendForAllUsers(TOP_CANDIDATES)

        candidates = candidates.select(
            col("USER_ID"),
            explode("recommendations").alias("recommendation"),
        )

        candidates = candidates.select(
    col("USER_ID"),
    col("recommendation.MOVIE_ID").alias("MOVIE_ID"),
    col("recommendation.rating").alias("PREDICTED_RATING"),
)

        # Exclude movies already rated
        print("\nRemoving previously rated movies...")

        unseen_movies = candidates.join(
            rated_movies,
            on=["USER_ID", "MOVIE_ID"],
            how="left_anti",
        )

        # Rank recommendations per user
        window = (
            Window
            .partitionBy("USER_ID")
            .orderBy(col("PREDICTED_RATING").desc())
        )

        recommendations = (
            unseen_movies
            .withColumn(
                "RECOMMENDATION_RANK",
                row_number().over(window),
            )
            .filter(col("RECOMMENDATION_RANK") <= TOP_RECOMMENDATIONS)
            .select(
                "USER_ID",
                "MOVIE_ID",
                "PREDICTED_RATING",
                "RECOMMENDATION_RANK",
            )
        )

        # Save to Snowflake
        print("\nSaving recommendations to Snowflake...")

        save_recommendations(recommendations)

        print("\nRecommendation generation completed!")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()