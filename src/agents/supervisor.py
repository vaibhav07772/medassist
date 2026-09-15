from agents.researcher import ResearcherAgent
from agents.summarizer import SummarizerAgent
from agents.safety_checker import SafetyCheckerAgent
import time

class MedAssistSupervisor:
    def __init__(self, vector_store):
        self.researcher = ResearcherAgent(vector_store)
        self.summarizer = SummarizerAgent()
        self.safety_checker = SafetyCheckerAgent()
        self.history = []

    def process(self, query: str) -> dict:
        """Run full MedAssist pipeline"""
        start_time = time.time()
        
        print("🔍 Researcher: Retrieving medical documents...")
        research = self.researcher.research(query, top_k=5)
        
        if not research["chunks"]:
            return {
                "query": query,
                "answer": "No relevant medical documents found in the database. Please upload medical documents first.",
                "sources": [],
                "is_safe": True,
                "is_emergency": False,
                "confidence": 0.0,
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
        
        print(f"✅ Found {len(research['chunks'])} relevant chunks")
        
        print("📝 Summarizer: Generating answer...")
        synthesis = self.summarizer.synthesize(
            query,
            research["context"],
            research["chunks"]
        )
        
        print("🛡️ Safety Checker: Validating...")
        safety = self.safety_checker.validate(
            query,
            synthesis["answer"],
            research["context"]
        )
        
        result = {
            "query": query,
            "answer": safety["final_answer"],
            "sources": research["chunks"],
            "citations": synthesis["citations"],
            "is_safe": safety["is_safe"],
            "is_emergency": safety["is_emergency"],
            "hallucination_score": safety["hallucination_score"],
            "issues": safety["issues"],
            "confidence": round(research["relevance_score"] * safety["hallucination_score"], 2),
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
        
        self.history.append(result)
        print(f"✅ Complete in {result['latency_ms']}ms")
        
        return result

    def get_history(self):
        return self.history