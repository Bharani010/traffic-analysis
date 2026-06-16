"""
PySpark Feature Engineering ETL Pipeline.

Reads raw traffic events, aggregates them by Session and IP address,
and computes security features (requests per minute, failed login rate,
endpoint entropy, etc.) for anomaly detection.
"""

import math
import os
import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DoubleType

from data.utils.spark_session import get_spark_session


def calculate_entropy(counts: dict) -> float:
    """Calculate Shannon entropy from a dictionary of counts."""
    if not counts:
        return 0.0
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)


def _compute_entropy_udf():
    """UDF to calculate entropy from an array of strings."""
    def _entropy(items: list[str]) -> float:
        if not items:
            return 0.0
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return calculate_entropy(counts)
    return F.udf(_entropy, DoubleType())


def aggregate_by_entity(df: DataFrame, entity_col: str, entity_type_label: str) -> DataFrame:
    """
    Aggregate raw events by a specific entity (e.g., session_id, ip_address)
    and compute engineered features.
    """
    
    # Filter out empty entity IDs
    df = df.filter(F.col(entity_col).isNotNull() & (F.col(entity_col) != ""))

    # 1. Group by the entity column
    grouped = df.groupBy(entity_col)

    # 2. Compute aggregate features
    agg_df = grouped.agg(
        # Basic stats
        F.count("*").alias("total_requests"),
        F.min("timestamp").alias("first_seen"),
        F.max("timestamp").alias("last_seen"),
        F.avg("response_time").alias("avg_response_time"),
        
        # Unique browsers/user agents
        F.countDistinct("browser").alias("unique_user_agents"),
        
        # Country switching
        F.countDistinct("country").alias("country_switch_frequency"),
        
        # Collect endpoints for entropy calculation
        F.collect_list("endpoint").alias("endpoint_list"),
        
        # Failed login tracking
        F.sum(
            F.when((F.col("endpoint") == "/api/v1/auth/login") & (F.col("status_code") == 401), 1).otherwise(0)
        ).alias("failed_logins"),
        F.sum(
            F.when(F.col("endpoint") == "/api/v1/auth/login", 1).otherwise(0)
        ).alias("total_logins"),
    )

    # 3. Derive complex features
    
    # Session duration (in seconds)
    agg_df = agg_df.withColumn(
        "session_duration",
        F.unix_timestamp("last_seen") - F.unix_timestamp("first_seen")
    )
    
    # Requests per minute
    # Avoid division by zero by setting minimum duration to 60 seconds for calculation
    agg_df = agg_df.withColumn(
        "duration_minutes",
        F.when(F.col("session_duration") < 60, 1.0).otherwise(F.col("session_duration") / 60.0)
    )
    agg_df = agg_df.withColumn(
        "requests_per_minute",
        F.col("total_requests") / F.col("duration_minutes")
    )
    
    # Failed login rate
    agg_df = agg_df.withColumn(
        "failed_login_rate",
        F.when(F.col("total_logins") > 0, F.col("failed_logins") / F.col("total_logins")).otherwise(0.0)
    )

    # Endpoint entropy
    entropy_udf = _compute_entropy_udf()
    agg_df = agg_df.withColumn("endpoint_entropy", entropy_udf(F.col("endpoint_list")))

    # 4. Select and format final feature table matching the schema
    # Features table: id, created_at, entity_type, entity_id, requests_per_minute, etc.
    final_df = agg_df.select(
        F.expr("uuid()").alias("id"),
        F.current_timestamp().alias("created_at"),
        F.lit(entity_type_label).alias("entity_type"),
        F.col(entity_col).alias("entity_id"),
        F.round("requests_per_minute", 2).alias("requests_per_minute"),
        F.round("failed_login_rate", 2).alias("failed_login_rate"),
        F.round("avg_response_time", 2).alias("avg_response_time"),
        F.round("endpoint_entropy", 4).alias("endpoint_entropy"),
        F.col("session_duration").cast("float").alias("session_duration"),
        F.col("country_switch_frequency").cast("float").alias("country_switch_frequency"),
        F.col("unique_user_agents").cast("int").alias("unique_user_agents")
    )

    return final_df


def process_events(spark: SparkSession, input_path: str, output_path: str) -> None:
    """Run the batch ETL pipeline."""
    print(f"Reading raw events from: {input_path}")
    df = spark.read.parquet(input_path)
    
    print(f"Total raw events loaded: {df.count()}")
    
    print("Computing Session-level features...")
    session_features = aggregate_by_entity(df, "session_id", "session")
    
    print("Computing IP-level features...")
    ip_features = aggregate_by_entity(df, "ip_address", "ip")
    
    # Combine features into a single dataset
    all_features = session_features.unionByName(ip_features)
    
    print(f"Total engineered features generated: {all_features.count()}")
    print("Feature summary statistics:")
    all_features.select(
        "requests_per_minute", "failed_login_rate", "endpoint_entropy", 
        "unique_user_agents", "country_switch_frequency"
    ).summary().show()
    
    # Fix for Windows local testing: PySpark writing Parquet requires Hadoop winutils.
    # We will convert to Pandas to write the final feature dataset smoothly.
    os.makedirs(output_path, exist_ok=True)
    parquet_path = os.path.join(output_path, "features.parquet")
    print(f"Writing features to: {parquet_path}")
    pdf = all_features.toPandas()
    pdf.to_parquet(parquet_path, engine="pyarrow", index=False)
    print("Feature engineering complete!")


if __name__ == "__main__":
    spark = get_spark_session("TrafficETL")
    
    # Default paths for local development
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "output", "traffic_events.parquet")
    output_dir = os.path.join(base_dir, "output")
    
    if os.path.exists(input_dir):
        process_events(spark, input_dir, output_dir)
    else:
        print(f"Input path not found: {input_dir}. Please run the simulation first.")
        
    spark.stop()
