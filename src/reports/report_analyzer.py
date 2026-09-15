from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os

class ReportAnalyzer:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def analyze_text_report(self, report_text: str) -> dict:
        """Analyze lab report text"""
        prompt = f"""
        You are a medical report analyst. Analyze this lab report.

        Report:
        {report_text[:3000]}

        Provide:
        1. Summary of key findings
        2. Abnormal values (if any)
        3. Possible implications
        4. Recommended next steps

        IMPORTANT: Never diagnose. Only summarize and suggest consulting a doctor.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = response.content
        except Exception as e:
            analysis = f"Error: {e}"
        
        return {
            "report_text": report_text[:500],
            "analysis": analysis,
            "disclaimer": "⚠️ This analysis is for educational purposes only. Consult a doctor."
        }

    def analyze_image_report(self, image_path: str) -> dict:
        """Analyze lab report image (requires Gemini Vision)"""
        try:
            import google.generativeai as genai
            from PIL import Image
            
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-pro-vision")
            
            img = Image.open(image_path)
            prompt = """
            Extract text from this medical report and analyze it.
            Provide summary + abnormal values + recommendations.
            """
            
            response = model.generate_content([prompt, img])
            return {
                "analysis": response.text,
                "source": "image",
                "disclaimer": "⚠️ Consult a doctor for interpretation."
            }
        except Exception as e:
            return {
                "analysis": f"Image analysis not available: {e}",
                "source": "image",
                "disclaimer": "⚠️ Please provide text report."
            }