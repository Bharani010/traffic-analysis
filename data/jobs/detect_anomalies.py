"""
Anomaly detection Spark job.

Applies rule-based and statistical anomaly detection on processed
traffic events. ML model integration planned for Phase 3+.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from data.utils.spark_session import get_spark_session


def detect_high_request_rate(df: DataFrame, threshold: int = 100) -> DataFrame:
    """Flag IPs with request rates above the threshold (rule-based)."""
    return df.withColumn(
        "is_high_rate_anomaly",
        F.when(F.col("requests_per_5min") > threshold, True).otherwise(False),
    )


def detect_high_error_rate(df: DataFrame, threshold: float = 0.5) -> DataFrame:
    """Flag IPs with error rates above the threshold (rule-based)."""
    return df.withColumn(
        "is_high_error_anomaly",
        F.when(F.col("error_rate_5min") > threshold, True).otherwise(False),
    )


def detect_slow_responses(df: DataFrame, threshold_ms: float = 2000.0) -> DataFrame:
    """Flag requests with unusually slow response times (statistical)."""
    return df.withColumn(
        "is_slow_response_anomaly",
        F.when(F.col("response_time_ms") > threshold_ms, True).otherwise(False),
    )


def detect_off_hours_admin(df: DataFrame) -> DataFrame:
    """Flag admin endpoint access outside business hours (rule-based)."""
    return df.withColumn(
        "is_off_hours_admin_anomaly",
        F.when(
            (F.col("path").startswith("/admin"))
            & (~F.col("is_business_hours")),
            True,
        ).otherwise(False),
    )


def run_detection_pipeline(df: DataFrame) -> DataFrame:
    """
    Run all anomaly detection methods and produce a summary.

    Returns the original DataFrame augmented with anomaly flags
    and an aggregate is_anomaly column.
    """
    df = detect_high_request_rate(df)
    df = detect_high_error_rate(df)
    df = detect_slow_responses(df)
    df = detect_off_hours_admin(df)

    # Aggregate: any flag triggers overall anomaly
    df = df.withColumn(
        "is_anomaly",
        F.col("is_high_rate_anomaly")
        | F.col("is_high_error_anomaly")
        | F.col("is_slow_response_anomaly")
        | F.col("is_off_hours_admin_anomaly"),
    )

    return df


if __name__ == "__main__":
    spark = get_spark_session("AnomalyDetector")

    # In production:
    # df = spark.read.parquet("s3://bucket/processed-events/")
    # result = run_detection_pipeline(df)
    # anomalies = result.filter(F.col("is_anomaly"))
    # anomalies.write.parquet("s3://bucket/anomalies/")

    print("Anomaly detector ready. Configure data sources for production use.")
    spark.stop()
