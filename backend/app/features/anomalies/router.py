"""
FastAPI Router for Anomalies and Investigations.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
import json
import os

from app.features.anomalies.agents import InvestigationAgent

router = APIRouter()


@router.get("/anomalies")
async def get_anomalies() -> dict[str, Any]:
    """Retrieve all detected anomalies. In this simplified version, we read from the JSON output."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    json_path = os.path.join(base_dir, "data", "output", "anomalies.json")
    
    if not os.path.exists(json_path):
        return {"data": []}
        
    with open(json_path, "r") as f:
        data = json.load(f)
        
    return {"data": data}


@router.post("/anomalies/{anomaly_id}/investigate")
async def investigate_anomaly(anomaly_id: str) -> dict[str, Any]:
    """Trigger the LangChain LLM agent to investigate an anomaly and generate a report."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    json_path = os.path.join(base_dir, "data", "output", "anomalies.json")
    
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Anomalies data not found")
        
    with open(json_path, "r") as f:
        data = json.load(f)
        
    target = next((a for a in data if a["id"] == anomaly_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Anomaly not found")
        
    agent = InvestigationAgent()
    report = agent.investigate(target)
    
    return {
        "anomaly_id": anomaly_id,
        "report": report
    }
