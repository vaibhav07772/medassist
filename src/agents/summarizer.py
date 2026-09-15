from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os

class SummarizerAgent:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def synthesize(self, query: str, context: str, chunks: list) -> dict:
        """Generate structured medical answer with citations"""
        system_prompt = """You are a medical information assistant. 
        Provide accurate, well-cited answers based ONLY on the provided context.
        
        IMPORTANT RULES:
        1. Only use information from the provided context
        2. Cite sources as [1], [2], etc.
        3. If information is not in context, say "Not available in provided documents"
        4. Use structured format (headings, bullets)
        5. Include a "Confidence: X%" at the end
        6. Never give medical advice - only summarize research
        """
        
        prompt = f"""
        Question: {query}

        Retrieved Medical Context:
        {context[:3000]}

        Provide a structured answer with:
        1. Direct Answer (2-3 sentences)
        2. Key Details (bullet points)
        3. Citations [1], [2], etc.
        4. Confidence Level
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {e}"
        
        # Extract citations used
        import re
        citations = re.findall(r'\[(\d+)\]', answer)
        cited_sources = []
        for c in set(citations):
            idx = int(c) - 1
            if 0 <= idx < len(chunks):
                cited_sources.append({
                    "index": c,
                    "source": chunks[idx]["metadata"].get("source", "unknown"),
                    "similarity": chunks[idx]["similarity"]
                })
        
        return {
            "answer": answer,
            "citations": cited_sources,
            "sources_used": len(cited_sources)
        }