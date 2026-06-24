"""
Anomaly Detection Engine.

Reads the engineered features from PySpark, runs rule-based heuristics
and an Isolation Forest ML model to flag suspicious sessions and IPs.
"""

import os
import uuid
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest


def detect_anomalies(features_df: pd.DataFrame) -> pd.DataFrame:
    """Run detection heuristics and ML models on features."""
    anomalies = []

    # 1. Rule-Based Detection
    for _, row in features_df.iterrows():
        entity = row['entity_id']
        entity_type = row['entity_type']
        
        # Rule 1: High Failed Login Rate (Credential Stuffing / Brute Force)
        if row['failed_login_rate'] > 0.5 and row['requests_per_minute'] > 5:
            anomalies.append({
                "id": str(uuid.uuid4()),
                "title": f"High Failed Login Rate on {entity_type} {entity}",
                "description": f"Failed login rate of {row['failed_login_rate']:.2f} with {row['requests_per_minute']:.2f} req/min.",
                "severity": "high",
                "detection_method": "rule_based",
                "status": "open",
                "confidence_score": 0.95,
                "source_ip": entity if entity_type == 'ip' else None,
                "affected_endpoint": "/api/v1/auth/login",
                "event_count": int(row['requests_per_minute'] * row['session_duration'] / 60) if row['session_duration'] > 0 else 10,
                "feature_id": row['id'],
                "created_at": datetime.utcnow().isoformat()
            })

        # Rule 2: API Abuse (High volume, low entropy)
        if row['requests_per_minute'] > 100 and row['endpoint_entropy'] < 0.5:
            anomalies.append({
                "id": str(uuid.uuid4()),
                "title": f"API Abuse / DoS from {entity_type} {entity}",
                "description": f"Extremely high request rate ({row['requests_per_minute']:.2f} req/min) targeting a narrow set of endpoints (entropy: {row['endpoint_entropy']:.2f}).",
                "severity": "critical",
                "detection_method": "rule_based",
                "status": "open",
                "confidence_score": 0.98,
                "source_ip": entity if entity_type == 'ip' else None,
                "affected_endpoint": "multiple",
                "event_count": int(row['requests_per_minute']),
                "feature_id": row['id'],
                "created_at": datetime.utcnow().isoformat()
            })
            
        # Rule 3: Session Hijacking / Geo Takeover
        if row['country_switch_frequency'] > 2:
            anomalies.append({
                "id": str(uuid.uuid4()),
                "title": f"Geographic Account Takeover / Session Hijacking on {entity}",
                "description": f"Session changed countries {row['country_switch_frequency']} times.",
                "severity": "high",
                "detection_method": "rule_based",
                "status": "open",
                "confidence_score": 0.85,
                "source_ip": entity if entity_type == 'ip' else None,
                "affected_endpoint": "all",
                "event_count": 1,
                "feature_id": row['id'],
                "created_at": datetime.utcnow().isoformat()
            })

        # Rule 4: Bot Crawling
        # Signature: medium-high velocity + zero login attempts + low endpoint entropy.
        # Bots that scrape browse endpoints at a steady pace never touch /auth/login,
        # so failed_login_rate == 0. Their endpoint spread is also compressed (only
        # browse subcategory), giving entropy below 1.5. This compound rule was added
        # after the Isolation Forest (calibrated at contamination=0.01) was
        # systematically missing bot crawling due to the model being tuned for a
        # lower anomaly rate than the actual 5% injection ratio.
        if (row['requests_per_minute'] > 30
                and row['endpoint_entropy'] < 1.5
                and row['failed_login_rate'] == 0.0):
            anomalies.append({
                "id": str(uuid.uuid4()),
                "title": f"Bot Crawling Detected on {entity_type} {entity}",
                "description": (
                    f"Medium-velocity scraping ({row['requests_per_minute']:.2f} req/min) "
                    f"with zero login attempts and compressed endpoint entropy "
                    f"({row['endpoint_entropy']:.2f}). Consistent with automated "
                    f"crawling targeting browse endpoints."
                ),
                "severity": "medium",
                "detection_method": "rule_based",
                "status": "open",
                "confidence_score": 0.80,
                "source_ip": entity if entity_type == 'ip' else None,
                "affected_endpoint": "multiple browse endpoints",
                "event_count": int(row['requests_per_minute']),
                "feature_id": row['id'],
                "created_at": datetime.utcnow().isoformat()
            })

    # 2. ML-Based Detection (Isolation Forest)
    # Train an unsupervised Isolation Forest on continuous features
    ml_features = ['requests_per_minute', 'failed_login_rate', 'avg_response_time', 
                   'endpoint_entropy', 'session_duration']
    
    X = features_df[ml_features].fillna(0)
    
    if len(X) > 10:
        model = IsolationForest(contamination=0.01, random_state=42)
        features_df['ml_anomaly'] = model.fit_predict(X)
        features_df['ml_score'] = model.decision_function(X)
        
        # -1 indicates anomaly
        ml_anomalies_df = features_df[features_df['ml_anomaly'] == -1]
        
        for _, row in ml_anomalies_df.iterrows():
            entity = row['entity_id']
            # Only add if we don't have overlapping severe rule anomalies for simplicity, 
            # or just add them all and let Incident aggregation handle it.
            score = float(-row['ml_score']) # Convert to positive risk score
            anomalies.append({
                "id": str(uuid.uuid4()),
                "title": f"Statistical Traffic Anomaly on {row['entity_type']} {entity}",
                "description": f"Isolation Forest detected highly unusual feature combination. Score: {score:.3f}.",
                "severity": "medium",
                "detection_method": "ml_model",
                "status": "open",
                "confidence_score": min(0.5 + score, 0.99),
                "source_ip": entity if row['entity_type'] == 'ip' else None,
                "affected_endpoint": "multiple",
                "event_count": 1,
                "feature_id": row['id'],
                "created_at": datetime.utcnow().isoformat()
            })

    return pd.DataFrame(anomalies)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, "output", "features.parquet")
    output_path = os.path.join(base_dir, "output", "anomalies.json")
    
    if not os.path.exists(input_path):
        print(f"Error: Features file not found at {input_path}")
        exit(1)
        
    print(f"Loading features from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"Loaded {len(df)} feature records.")
    
    print("Running detection engine (Rules + ML)...")
    anomalies_df = detect_anomalies(df)
    
    if not anomalies_df.empty:
        print(f"Detected {len(anomalies_df)} anomalies!")
        
        print("\nBreakdown by severity:")
        print(anomalies_df['severity'].value_counts())
        
        print("\nBreakdown by method:")
        print(anomalies_df['detection_method'].value_counts())
        
        print(f"\nSaving anomalies to {output_path}...")
        anomalies_df.to_json(output_path, orient='records', indent=2)
    else:
        print("No anomalies detected.")
