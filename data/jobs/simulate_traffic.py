"""
Realistic web traffic simulator.

Generates synthetic HTTP traffic events with configurable patterns,
including normal traffic, burst patterns, and anomalous behavior.
"""

import random
import uuid
from datetime import datetime, timezone

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from data.schemas.traffic_event import TRAFFIC_EVENT_SCHEMA
from data.utils.spark_session import get_spark_session

# ── Configuration ──

NORMAL_IPS = [f"192.168.1.{i}" for i in range(1, 51)]
SUSPICIOUS_IPS = ["10.99.99.1", "10.99.99.2", "172.16.0.100"]
ENDPOINTS = [
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/orders",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/search",
    "/api/v1/health",
    "/admin/dashboard",
    "/admin/settings",
]
METHODS = ["GET", "GET", "GET", "POST", "PUT", "DELETE"]  # Weighted toward GET
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0",
    "python-requests/2.31.0",
    "curl/8.4.0",
]
COUNTRY_CODES = ["US", "GB", "DE", "FR", "JP", "CN", "BR", "IN", "AU", "CA"]


def generate_normal_event() -> dict:
    """Generate a single normal traffic event."""
    return {
        "id": str(uuid.uuid4()),
        "source_ip": random.choice(NORMAL_IPS),
        "destination_ip": "10.0.0.1",
        "method": random.choice(METHODS),
        "path": random.choice(ENDPOINTS),
        "user_agent": random.choice(USER_AGENTS),
        "status_code": random.choices(
            [200, 201, 301, 400, 403, 404, 500],
            weights=[70, 5, 5, 5, 3, 10, 2],
            k=1,
        )[0],
        "response_time_ms": round(random.gauss(100, 30), 2),
        "bytes_sent": random.randint(200, 50000),
        "bytes_received": random.randint(100, 5000),
        "country_code": random.choice(COUNTRY_CODES),
        "session_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc),
    }


def generate_anomalous_event() -> dict:
    """Generate a suspicious traffic event for anomaly detection testing."""
    event = generate_normal_event()
    anomaly_type = random.choice(["brute_force", "scraping", "ddos", "injection"])

    if anomaly_type == "brute_force":
        event["source_ip"] = random.choice(SUSPICIOUS_IPS)
        event["path"] = "/api/v1/auth/login"
        event["method"] = "POST"
        event["status_code"] = 401
        event["response_time_ms"] = round(random.gauss(20, 5), 2)
    elif anomaly_type == "scraping":
        event["source_ip"] = random.choice(SUSPICIOUS_IPS)
        event["response_time_ms"] = round(random.gauss(10, 3), 2)
        event["user_agent"] = "python-requests/2.31.0"
    elif anomaly_type == "ddos":
        event["source_ip"] = random.choice(SUSPICIOUS_IPS)
        event["response_time_ms"] = round(random.gauss(5000, 1000), 2)
        event["status_code"] = 503
    elif anomaly_type == "injection":
        event["path"] = "/api/v1/search?q=' OR 1=1 --"
        event["status_code"] = 400

    return event


def simulate_traffic(
    spark: SparkSession,
    num_events: int = 10000,
    anomaly_ratio: float = 0.05,
) -> DataFrame:
    """
    Generate a DataFrame of simulated traffic events.

    Args:
        spark: Active SparkSession
        num_events: Total number of events to generate
        anomaly_ratio: Fraction of events that should be anomalous (0.0 - 1.0)

    Returns:
        Spark DataFrame with traffic events
    """
    num_anomalous = int(num_events * anomaly_ratio)
    num_normal = num_events - num_anomalous

    events = [generate_normal_event() for _ in range(num_normal)]
    events.extend([generate_anomalous_event() for _ in range(num_anomalous)])
    random.shuffle(events)

    return spark.createDataFrame(events, schema=TRAFFIC_EVENT_SCHEMA)


if __name__ == "__main__":
    spark = get_spark_session("TrafficSimulator")
    df = simulate_traffic(spark, num_events=100000, anomaly_ratio=0.05)
    print(f"Generated {df.count()} traffic events")
    df.show(20, truncate=False)
    spark.stop()
