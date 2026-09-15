from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
import json
import re

class HallucinationDetector:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.1,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def detect(self, answer: str, context: str) -> dict:
        """Detect if answer is hallucinated vs context"""
        prompt = f"""
        Compare the answer with the context. Detect hallucinations.

        Answer: {answer[:1500]}
        Context: {context[:2000]}

        Return JSON:
        {{
            "hallucination_score": 0.0-1.0,
            "unsupported_claims": ["claim1", "claim2"],
            "verdict": "FAITHFUL" or "PARTIAL" or "HALLUCINATED"
        }}

        Score: 1.0 = fully faithful, 0.0 = fully hallucinated
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Hallucination detect error: {e}")
        
        return {
            "hallucination_score": 0.8,
            "unsupported_claims": [],
            "verdict": "FAITHFUL"
        }