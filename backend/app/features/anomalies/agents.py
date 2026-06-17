"""
LangChain-powered LLM Investigation Agents.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# MUST load .env before importing LangChain/Groq so API keys are available
_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(_ROOT / ".env", override=True)

import json
import random
import re
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class MockLLM:
    """A highly dynamic mock LLM that generates realistic, varied incident reports."""
    
    def invoke(self, messages: list) -> Any:
        try:
            content = messages[1].content
            # Use regex to safely extract just the JSON dictionary from the prompt string
            match = re.search(r"(\{.*\})", content, re.DOTALL)
            if match:
                context = json.loads(match.group(1))
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            print(f"MockLLM Parse Error: {e}")
            context = {"title": "Unknown", "severity": "medium", "description": "Suspicious traffic"}

        method = context.get('detection_method', 'heuristics')
        severity = str(context.get('severity', 'medium')).upper()
        entity = context.get('source_ip') or 'Unknown Entity'
        title = context.get('title', 'Suspicious Activity')
        
        # Varied introductory paragraphs
        intros = [
            f"During routine traffic analysis, the AI engine flagged **{title}**. The activity was isolated using {method} and has been classified as {severity} priority.",
            f"**Executive Summary:** A {severity} severity incident was generated after {method} detected anomalous behavior matching the profile of '{title}'.",
            f"The platform's {method} pipeline has triggered an alert for {entity}. This {severity}-level anomaly indicates a potential ongoing security event: {title}."
        ]
        
        # Varied findings based on method
        if method == "ml_model":
            findings = [
                f"- The Isolation Forest algorithm placed this session in the 99th percentile of outlier traffic.\n- Traffic features (duration, endpoint entropy, request volume) deviated significantly from the established baseline for {entity}.",
                f"- Statistical deviation detected in request frequencies.\n- The model confidence score is {(context.get('confidence_score', 0.9) * 100):.1f}%, indicating a highly abnormal cluster of events compared to historical norms.",
                f"- Unsupervised ML flagged the feature vector for this session.\n- {context.get('description', 'Unusual combinations of API calls were observed.')}"
            ]
        else:
            findings = [
                f"- Hardcoded heuristic thresholds were exceeded.\n- {context.get('description', 'High velocity of requests.')}\n- Affected endpoint: `{context.get('affected_endpoint', 'multiple')}`.",
                f"- Signature match: The behavior of {entity} matches known attack vectors.\n- Total events recorded in this burst: {context.get('event_count', 'multiple')}.",
                f"- {context.get('description', 'Suspicious activity logged.')}\n- The traffic patterns lack the typical delays and variance of human navigation, strongly suggesting automation."
            ]

        # Varied mitigations
        mitigations = [
            f"- **Immediate:** Block IP {entity} at the WAF level for 24 hours.\n- **Secondary:** Force password resets for any accounts accessed during this window.",
            f"- Apply aggressive rate-limiting to `{context.get('affected_endpoint', 'API')}`.\n- Dispatch the logs for {entity} to the SIEM for cross-referencing with threat intel feeds.",
            f"- Isolate the affected sessions and terminate active JWT tokens.\n- Implement a CAPTCHA challenge for traffic originating from the subnet of {entity}.",
            f"- No immediate blocking required, but add {entity} to the proactive watch-list.\n- Review threshold rules for `{method}` if this is deemed benign."
        ]

        # Use instance variable (not class variable) so f-string evaluates fresh each call
        class MockResponse:
            def __init__(self):
                self.content = f"""
### AI Incident Investigation Report
**Severity Rating:** {severity}
**Entity Tracked:** `{entity}`

**1. Incident Overview**
{random.choice(intros)}

**2. Core Findings & Behavioral Analysis**
{random.choice(findings)}

**3. Recommended Mitigation Strategy**
{random.choice(mitigations)}
                """
        return MockResponse()


class InvestigationAgent:
    """Autonomous agent for investigating traffic anomalies."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        else:
            print("WARNING: GROQ_API_KEY not set. Using MockLLM for investigations.")
            self.llm = MockLLM() # type: ignore

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Cybersecurity Incident Responder. Analyze the provided anomaly data and generate a clear, concise, and structured incident report with Findings and Mitigation steps."),
            ("human", "Anomaly Details:\n{anomaly_data}\n\nPlease generate the incident report.")
        ])

    def investigate(self, anomaly_record: Dict[str, Any]) -> str:
        """
        Run the investigation workflow on a specific anomaly.
        
        Args:
            anomaly_record: A dictionary containing anomaly details (e.g. from detect_anomalies output)
            
        Returns:
            A formatted markdown string containing the incident report.
        """
        # In a real enterprise system, the agent would use LangChain Tools to query 
        # the database for historical context. For this portfolio version, we pass the context directly.
        
        context = json.dumps(anomaly_record, indent=2)
        messages = self.prompt_template.format_messages(anomaly_data=context)
        
        response = self.llm.invoke(messages)
        return str(response.content)


if __name__ == "__main__":
    # Test script
    agent = InvestigationAgent()
    
    test_anomaly = {
        "title": "High Failed Login Rate on ip 192.168.1.100",
        "description": "Failed login rate of 0.85 with 12.5 req/min.",
        "severity": "high",
        "affected_endpoint": "/api/v1/auth/login"
    }
    
    print("Running LLM Investigation...")
    report = agent.investigate(test_anomaly)
    print("\n" + "="*50)
    print(report)
    print("="*50 + "\n")
