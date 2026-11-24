import tomllib
from pathlib import Path

import pandas as pd
import snowflake.connector

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator


# --------------------------------------------------
# Snowflake Connection
# --------------------------------------------------

def get_snowflake_connection():
    project_dir = Path(__file__).resolve().parents[1]

    secrets_path = (
        project_dir
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
# Load Ratings from Snowflake
# --------------------------------------------------

def load_ratings():
    connection = get_snowflake_connection()

    query = """
        SELECT
            USER_ID,
            MOVIE_ID,
            RATING
        FROM MOVIELENS.DEV.FCT_RATINGS
        WHERE USER_ID IS NOT NULL
          AND MOVIE_ID IS NOT NULL
          AND RATING IS NOT NULL
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query)

        ratings_pdf = cursor.fetch_pandas_all()

        print(f"Loaded {len(ratings_pdf):,} ratings from Snowflake")

        return ratings_pdf

    finally:
        connection.close()


# --------------------------------------------------
# Train ALS Model
# --------------------------------------------------

def main():

    spark = (
        SparkSession.builder
        .appName("MovieLens-ALS-Recommendation")
        .master("local[4]")
        .config("spark.driver.memory", "5g")
        .config("spark.driver.maxResultSize", "1g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.default.parallelism", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:

        # Load data
        print("\nLoading ratings from Snowflake...")

        ratings_pdf = load_ratings()

        print(f"Loaded {len(ratings_pdf):,} ratings")

        # Convert Pandas DataFrame to Spark DataFrame
        ratings = spark.createDataFrame(ratings_pdf).select(
            col("USER_ID").cast("int"),
            col("MOVIE_ID").cast("int"),
            col("RATING").cast("float"),
        )

        del ratings_pdf

        print("\nRatings DataFrame:")
        print(f"Total ratings: {ratings.count():,}")

        # Train/Test Split
        train, test = ratings.randomSplit(
            [0.8, 0.2],
            seed=42
        )

        print(f"Training records: {train.count():,}")
        print(f"Testing records: {test.count():,}")

        # ALS Configuration
        als = ALS(
            userCol="USER_ID",
            itemCol="MOVIE_ID",
            ratingCol="RATING",
            implicitPrefs=False,
            rank=10,
            maxIter=5,
            regParam=0.1,
            coldStartStrategy="drop",
            nonnegative=True,
            seed=42,
            numUserBlocks=8,
            numItemBlocks=8,
        )

        # Train
        print("\nTraining ALS model...")

        model = als.fit(train)

        print("Training completed!")

        # Evaluate
        print("\nEvaluating model...")

        predictions = model.transform(test)

        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="RATING",
            predictionCol="prediction",
        )

        rmse = evaluator.evaluate(predictions)

        print(f"\nTest RMSE: {rmse:.4f}")

        # Save Model
        model_path = (
            Path(__file__).resolve().parent / "als_model"
        )

        model.write().overwrite().save(str(model_path))

        print(f"\nModel saved to: {model_path}")

        predictions.unpersist()
        train.unpersist()
        test.unpersist()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()