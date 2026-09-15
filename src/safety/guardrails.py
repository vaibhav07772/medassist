import re

class Guardrails:
    def __init__(self):
        self.emergency_keywords = [
            "chest pain", "heart attack", "stroke", "suicide",
            "overdose", "severe bleeding", "difficulty breathing",
            "unconscious", "seizure", "anaphylaxis", "poisoning"
        ]
        
        self.banned_patterns = [
            r"\b\d{10}\b",           # Phone numbers
            r"\b\d{3}-\d{2}-\d{4}\b", # SSN
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email
        ]

    def check_input(self, query: str) -> dict:
        """Validate input query"""
        query_lower = query.lower()
        
        is_emergency = any(kw in query_lower for kw in self.emergency_keywords)
        
        # Check for PII
        has_pii = any(re.search(p, query) for p in self.banned_patterns)
        
        return {
            "is_emergency": is_emergency,
            "has_pii": has_pii,
            "is_safe": not has_pii,
            "recommendation": "Emergency detected" if is_emergency else "Safe"
        }

    def check_output(self, answer: str) -> dict:
        """Validate output answer"""
        has_pii = any(re.search(p, answer) for p in self.banned_patterns)
        
        return {
            "has_pii": has_pii,
            "is_safe": not has_pii,
            "action": "Redact PII" if has_pii else "Pass"
        }

    def add_disclaimer(self, answer: str) -> str:
        """Add medical disclaimer"""
        disclaimer = """

---
⚠️ **MEDICAL DISCLAIMER**
This information is for educational purposes only.
Consult a qualified healthcare provider for medical advice.
"""
        return answer + disclaimer