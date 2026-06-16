"""
Spark schema definitions for traffic events.
"""

from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

TRAFFIC_EVENT_SCHEMA = StructType(
    [
        StructField("id", StringType(), nullable=False),
        StructField("source_ip", StringType(), nullable=False),
        StructField("destination_ip", StringType(), nullable=False),
        StructField("method", StringType(), nullable=False),
        StructField("path", StringType(), nullable=False),
        StructField("user_agent", StringType(), nullable=True),
        StructField("status_code", IntegerType(), nullable=False),
        StructField("response_time_ms", FloatType(), nullable=False),
        StructField("bytes_sent", IntegerType(), nullable=False),
        StructField("bytes_received", IntegerType(), nullable=False),
        StructField("country_code", StringType(), nullable=True),
        StructField("session_id", StringType(), nullable=True),
        StructField("timestamp", TimestampType(), nullable=False),
    ]
)
