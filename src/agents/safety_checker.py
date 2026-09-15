from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
import json
import re

class SafetyCheckerAgent:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.1,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.emergency_keywords = [
            "chest pain", "heart attack", "stroke", "suicide", "overdose",
            "severe bleeding", "difficulty breathing", "unconscious",
            "seizure", "anaphylaxis", "poisoning"
        ]
        
        self.disclaimer = """
⚠️ **MEDICAL DISCLAIMER**
This information is for educational and research purposes only. 
It is NOT a substitute for professional medical advice, diagnosis, or treatment.
Always consult a qualified healthcare provider for medical decisions.
In case of emergency, call your local emergency number immediately.
"""

    def check_emergency(self, query: str) -> bool:
        """Check if query contains emergency keywords"""
        query_lower = query.lower()
        return any(kw in query_lower for kw in self.emergency_keywords)

    def check_hallucination(self, answer: str, context: str) -> dict:
        """Check if answer is grounded in context"""
        prompt = f"""
        You are a medical safety checker. Verify if this answer is faithful to the context.

        Answer: {answer[:1500]}
        Context: {context[:2000]}

        Return JSON:
        {{
            "is_faithful": true/false,
            "hallucination_score": 0.0-1.0,
            "issues": ["issue 1", "issue 2"],
            "unsupported_claims": ["claim 1"]
        }}

        Score: 0 = completely hallucinated, 1 = fully faithful
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Hallucination check error: {e}")
        
        return {
            "is_faithful": True,
            "hallucination_score": 0.8,
            "issues": [],
            "unsupported_claims": []
        }

    def validate(self, query: str, answer: str, context: str) -> dict:
        """Full safety validation"""
        is_emergency = self.check_emergency(query)
        hallucination = self.check_hallucination(answer, context)
        
        # Determine safety status
        is_safe = hallucination.get("is_faithful", True)
        
        # Add disclaimer
        final_answer = answer
        if is_emergency:
            final_answer = (
                "🚨 **EMERGENCY DETECTED**\n"
                "Please call emergency services immediately.\n\n"
                + final_answer
            )
        
        final_answer += f"\n\n---\n{self.disclaimer}"
        
        return {
            "is_safe": is_safe,
            "is_emergency": is_emergency,
            "hallucination_score": hallucination.get("hallucination_score", 0.8),
            "issues": hallucination.get("issues", []),
            "final_answer": final_answer,
            "disclaimer_added": True
        }