"""
Event processing ETL pipeline.

Reads raw traffic events, enriches them with computed features,
and writes processed results for downstream analysis.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from data.utils.spark_session import get_spark_session


def add_time_features(df: DataFrame) -> DataFrame:
    """Add time-based features for pattern analysis."""
    return df.withColumns(
        {
            "hour_of_day": F.hour("timestamp"),
            "day_of_week": F.dayofweek("timestamp"),
            "is_business_hours": F.when(
                (F.hour("timestamp") >= 8) & (F.hour("timestamp") <= 18), True
            ).otherwise(False),
        }
    )


def add_request_rate_features(df: DataFrame) -> DataFrame:
    """Compute per-IP request rates over a sliding window."""
    window_spec = (
        Window.partitionBy("source_ip")
        .orderBy(F.col("timestamp").cast("long"))
        .rangeBetween(-300, 0)  # 5-minute window
    )
    return df.withColumn(
        "requests_per_5min",
        F.count("*").over(window_spec),
    )


def add_error_rate_features(df: DataFrame) -> DataFrame:
    """Compute error rates per source IP."""
    window_spec = (
        Window.partitionBy("source_ip")
        .orderBy(F.col("timestamp").cast("long"))
        .rangeBetween(-300, 0)
    )
    return df.withColumns(
        {
            "is_error": F.when(F.col("status_code") >= 400, 1).otherwise(0),
            "error_rate_5min": F.avg(
                F.when(F.col("status_code") >= 400, 1).otherwise(0)
            ).over(window_spec),
        }
    )


def process_events(df: DataFrame) -> DataFrame:
    """
    Full processing pipeline: enrich raw traffic with computed features.

    Pipeline steps:
    1. Add time-based features
    2. Add request rate features
    3. Add error rate features
    """
    df = add_time_features(df)
    df = add_request_rate_features(df)
    df = add_error_rate_features(df)
    return df


if __name__ == "__main__":
    spark = get_spark_session("EventProcessor")

    # In production, read from a data source
    # df = spark.read.parquet("s3://bucket/raw-events/")
    # processed = process_events(df)
    # processed.write.parquet("s3://bucket/processed-events/")

    print("Event processor ready. Configure data sources for production use.")
    spark.stop()
