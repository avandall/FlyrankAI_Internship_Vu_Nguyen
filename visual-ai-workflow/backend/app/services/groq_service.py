"""
Groq LLM Decision Service: Evaluates node prompt against input context and returns strictly YES or NO with reasoning.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional, Tuple
from app.models.workflow_schema import DecisionType

logger = logging.getLogger("visual_workflow.groq")

SYSTEM_PROMPT = """You are a precise AI Decision Node in a visual automated workflow.
Your task is to evaluate the given QUESTION / PROMPT against the provided INPUT CONTEXT.

RULES:
1. You must answer strictly with either "YES" or "NO".
2. You must provide a concise 1-2 sentence explanation of your reasoning.
3. Respond ONLY with a valid JSON object in the following format:
{
  "decision": "YES" or "NO",
  "reasoning": "brief explanation why YES or NO",
  "confidence": 0.95
}
"""

def evaluate_decision_node(
    prompt: str,
    input_text: str,
    system_instruction: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
) -> Tuple[DecisionType, str, float, float]:
    """
    Evaluates prompt and input_text using Groq API (or offline smart simulator if key missing).
    Returns (decision, reasoning, confidence, latency_ms).
    """
    start_time = time.time()
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)

            sys_inst = system_instruction if system_instruction else SYSTEM_PROMPT
            user_msg = f"PROMPT TO EVALUATE: {prompt}\n\nINPUT CONTEXT: {input_text}"

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_inst},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=150,
            )

            raw_content = response.choices[0].message.content or "{}"
            data = json.loads(raw_content)
            
            raw_decision = str(data.get("decision", "")).strip().upper()
            decision = DecisionType.YES if "YES" in raw_decision else DecisionType.NO
            reasoning = str(data.get("reasoning", "Evaluated by Groq LLM."))
            confidence = float(data.get("confidence", 0.95))
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            return decision, reasoning, confidence, latency_ms

        except Exception as e:
            logger.warning(f"Groq API call failed: {e}. Falling back to rule-based evaluation.")

    # Fallback / Offline Rule-based Heuristic Simulation
    time.sleep(0.08)  # simulate async LLM latency
    decision, reasoning = _simulate_decision(prompt, input_text)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    return decision, reasoning, 0.90, latency_ms


def _simulate_decision(prompt: str, input_text: str) -> Tuple[DecisionType, str]:
    """Offline heuristic engine that intelligently classifies standard workflows."""
    p_lower = prompt.lower()
    i_lower = input_text.lower()

    # Sentiment / Urgency checks
    if "urgent" in p_lower or "critical" in p_lower or "emergency" in p_lower:
        is_urgent = any(w in i_lower for w in ["urgent", "asap", "crash", "down", "outage", "broken", "critical", "immediately"])
        return (DecisionType.YES, "Input contains urgency keywords (e.g. crash/down/critical).") if is_urgent else (DecisionType.NO, "No urgent or critical indicators found in input.")

    # Support / Bug / Issue
    if "support" in p_lower or "bug" in p_lower or "error" in p_lower or "issue" in p_lower or "troubleshoot" in p_lower:
        is_support = any(w in i_lower for w in ["error", "fail", "bug", "crash", "help", "support", "broken", "issue", "problem", "cannot", "fix"])
        return (DecisionType.YES, "Input clearly describes a technical error or support issue.") if is_support else (DecisionType.NO, "Input does not appear to be a technical support inquiry.")

    # Sales / Pricing / Purchase
    if "sales" in p_lower or "pricing" in p_lower or "quote" in p_lower or "buy" in p_lower or "purchase" in p_lower:
        is_sales = any(w in i_lower for w in ["price", "cost", "quote", "buy", "purchase", "enterprise", "plan", "upgrade", "billing", "license"])
        return (DecisionType.YES, "Input expresses intent to purchase or inquiry about pricing.") if is_sales else (DecisionType.NO, "No sales or pricing intent detected.")

    # Technical / Code
    if "code" in p_lower or "technical" in p_lower or "api" in p_lower or "database" in p_lower:
        is_tech = any(w in i_lower for w in ["api", "sql", "code", "python", "endpoint", "database", "query", "server", "exception"])
        return (DecisionType.YES, "Technical or engineering terms are present.") if is_tech else (DecisionType.NO, "No technical terminology present.")

    # Default heuristic: check word overlaps
    keywords = [w for w in re.findall(r'\w+', p_lower) if len(w) > 3 and w not in ["this", "that", "what", "does", "have", "with"]]
    matches = [k for k in keywords if k in i_lower]
    if len(matches) > 0:
        return DecisionType.YES, f"Found semantic match for criteria keywords: {', '.join(matches[:3])}."
    return DecisionType.NO, "Criteria not satisfied based on input analysis."
