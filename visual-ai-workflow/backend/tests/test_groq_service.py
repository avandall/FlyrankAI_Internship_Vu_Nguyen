"""
Tests for Groq Decision Engine
"""

from app.models.workflow_schema import DecisionType
from app.services.groq_service import evaluate_decision_node


def test_groq_decision_urgent_support():
    decision, reasoning, confidence, latency = evaluate_decision_node(
        prompt="Is this an urgent support request?",
        input_text="CRITICAL: Our main payment API is down and throwing 500 errors!",
    )
    assert decision == DecisionType.YES
    assert len(reasoning) > 0
    assert latency > 0


def test_groq_decision_sales_intent():
    decision, reasoning, confidence, latency = evaluate_decision_node(
        prompt="Is the user asking for sales pricing?",
        input_text="Hi, I would like to get a quote for 500 enterprise seats.",
    )
    assert decision == DecisionType.YES
    assert "pricing" in reasoning.lower() or "purchase" in reasoning.lower() or "sales" in reasoning.lower() or "quote" in reasoning.lower()


def test_groq_decision_negative_case():
    decision, reasoning, confidence, latency = evaluate_decision_node(
        prompt="Is this message a bug report?",
        input_text="Thank you so much, your team did a fantastic job today!",
    )
    assert decision == DecisionType.NO
