"""
Spark schema definitions for traffic events.
"""

from pyspark.sql.types import (
    BooleanType,
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

TRAFFIC_EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), nullable=False),
        StructField("timestamp", TimestampType(), nullable=False),
        StructField("ip_address", StringType(), nullable=False),
        StructField("session_id", StringType(), nullable=True),
        StructField("user_id", StringType(), nullable=True),
        StructField("method", StringType(), nullable=False),
        StructField("endpoint", StringType(), nullable=False),
        StructField("category", StringType(), nullable=False),
        StructField("subcategory", StringType(), nullable=False),
        StructField("status_code", IntegerType(), nullable=False),
        StructField("response_time", FloatType(), nullable=False),
        StructField("request_size", IntegerType(), nullable=False),
        StructField("response_size", IntegerType(), nullable=False),
        StructField("country", StringType(), nullable=True),
        StructField("device", StringType(), nullable=True),
        StructField("browser", StringType(), nullable=True),
        StructField("is_attack", BooleanType(), nullable=False),
        StructField("attack_type", StringType(), nullable=False),
    ]
)
