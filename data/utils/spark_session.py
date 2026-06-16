"""
Spark session factory.

Creates a configured SparkSession with sensible defaults
for local development and production environments.
"""

import os

from pyspark.sql import SparkSession


def get_spark_session(
    app_name: str = "TrafficAnalysis",
    master: str | None = None,
) -> SparkSession:
    """
    Create or get an existing SparkSession.

    Args:
        app_name: Name of the Spark application
        master: Spark master URL. Defaults to SPARK_MASTER env var or local[*].

    Returns:
        Configured SparkSession
    """
    master = master or os.getenv("SPARK_MASTER", "local[*]")

    builder = (
        SparkSession.builder.appName(app_name)
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "2g"))
        .config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "2g"))
    )

    return builder.getOrCreate()
