from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
import json
import re

class ResearcherAgent:
    def __init__(self, vector_store, model="groq/compound-mini"):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model=model,
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def research(self, query: str, top_k: int = 5) -> dict:
        """Retrieve relevant medical information"""
        # Vector search
        chunks = self.vector_store.search(query, top_k=top_k)
        
        if not chunks:
            return {
                "query": query,
                "chunks": [],
                "summary": "No relevant medical documents found.",
                "confidence": 0.0
            }
        
        # Build context
        context = "\n\n".join([
            f"[Source {i+1}: {c['metadata'].get('source', 'unknown')}]\n{c['content']}"
            for i, c in enumerate(chunks)
        ])
        
        # LLM-based relevance check
        prompt = f"""
        You are a medical research assistant. Analyze if the following context is relevant to the query.

        Query: {query}
        Context: {context[:2000]}

        Return JSON:
        {{
            "is_relevant": true/false,
            "relevance_score": 0.0-1.0,
            "key_findings": ["finding 1", "finding 2"]
        }}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"is_relevant": True, "relevance_score": 0.7, "key_findings": []}
        except Exception as e:
            print(f"Research analysis error: {e}")
            analysis = {"is_relevant": True, "relevance_score": 0.7, "key_findings": []}
        
        return {
            "query": query,
            "chunks": chunks,
            "context": context,
            "is_relevant": analysis.get("is_relevant", True),
            "relevance_score": analysis.get("relevance_score", 0.7),
            "key_findings": analysis.get("key_findings", [])
        }