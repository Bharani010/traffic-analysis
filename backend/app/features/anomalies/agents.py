"""
LangChain-powered LLM Investigation Agents.

Responsible for autonomously investigating detected anomalies,
querying contextual data, and generating structured incident reports.
"""

import os
import json
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class MockLLM:
    """A mock LLM for portfolio/local testing without an API key."""
    
    def invoke(self, messages: list) -> Any:
        class MockResponse:
            content = """
### Automated Incident Report
**Incident Summary:**
The detection engine flagged a suspicious pattern originating from this entity. The behavioral signature strongly correlates with automated abuse or credential stuffing.

**Findings:**
1. High volume of requests targeting sensitive endpoints.
2. Low entropy in endpoint targets suggests an automated script rather than a human user.
3. Behavior deviates significantly from the established baseline profile.

**Recommended Mitigation:**
- Temporarily block or rate-limit the source IP.
- Invalidate active sessions for the affected user accounts.
- Enforce MFA for subsequent login attempts from this entity.
            """
        return MockResponse()


class InvestigationAgent:
    """Autonomous agent for investigating traffic anomalies."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        else:
            print("WARNING: OPENAI_API_KEY not set. Using MockLLM for investigations.")
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
