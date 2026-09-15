import streamlit as st
import sys
import os
from dotenv import load_dotenv
from safety.hallucination import HallucinationDetector
from safety.guardrails import Guardrails
from reports.report_analyzer import ReportAnalyzer

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.document_processor import DocumentProcessor
from ingestion.vector_store import MedicalVectorStore
from agents.supervisor import MedAssistSupervisor

st.set_page_config(page_title="🏥 MedAssist", layout="wide")

st.title("🏥 MedAssist — Clinical & Research Intelligence")
st.markdown("*Multi-Agent Medical RAG with Safety Layer*")

# Initialize
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = MedicalVectorStore()
if 'processor' not in st.session_state:
    st.session_state.processor = DocumentProcessor()
if 'supervisor' not in st.session_state:
    st.session_state.supervisor = MedAssistSupervisor(st.session_state.vector_store)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### 🤖 Agents")
    st.markdown("🔍 **Researcher** — RAG retrieval")
    st.markdown("📝 **Summarizer** — Answer generation")
    st.markdown("🛡️ **Safety Checker** — Hallucination detection")
    st.markdown("---")
    
    stats = st.session_state.vector_store.get_stats()
    st.metric("📚 Indexed Chunks", stats["total_chunks"])
    st.markdown("---")
    
    # Upload
    st.markdown("### 📤 Upload Medical Documents")
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_file and st.button("📥 Index Documents"):
        os.makedirs("data/documents", exist_ok=True)
        total_chunks = 0
        for file in uploaded_file:
            file_path = f"data/documents/{file.name}"
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            with st.spinner(f"Processing {file.name}..."):
                try:
                    processed = st.session_state.processor.process(file_path)
                    if processed:
                        chunks = st.session_state.vector_store.add_document(
                            processed["chunks"], processed["metadata"]
                        )
                        total_chunks += chunks
                        st.success(f"✅ {file.name}: {chunks} chunks")
                except Exception as e:
                    st.error(f"❌ {file.name}: {e}")
        
        if total_chunks > 0:
            st.success(f"✅ Total {total_chunks} chunks indexed!")
            st.rerun()

# Main area
query = st.text_area(
    "🔍 Ask a medical question",
    "What are the symptoms and treatment of type 2 diabetes?",
    height=100
)

if st.button("🚀 Run MedAssist", type="primary"):
    if query:
        with st.spinner("🧠 MedAssist is analyzing..."):
            result = st.session_state.supervisor.process(query)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Confidence", f"{result['confidence']*100:.0f}%")
        with col2:
            st.metric("Sources", len(result["sources"]))
        with col3:
            st.metric("Safety", "🛡️ Safe" if result["is_safe"] else "⚠️ Review")
        with col4:
            st.metric("Latency", f"{result['latency_ms']:.0f}ms")
        
        # Emergency alert
        if result.get("is_emergency"):
            st.error("🚨 **EMERGENCY KEYWORDS DETECTED** — Please seek immediate medical help!")
        
        st.markdown("---")
        st.subheader("📝 Answer")
        st.markdown(result["answer"])
        
        # Citations
        if result.get("citations"):
            with st.expander("📚 Citations"):
                for c in result["citations"]:
                    st.write(f"**[{c['index']}]** {c['source']} (similarity: {c['similarity']})")
        
        # Sources
        if result.get("sources"):
            with st.expander("📄 Source Chunks"):
                for i, s in enumerate(result["sources"]):
                    st.write(f"**[{i+1}]** {s['metadata'].get('source', 'unknown')}")
                    st.caption(s["content"][:300] + "...")
        
        # Safety issues
        if result.get("issues"):
            with st.expander("⚠️ Safety Issues"):
                for issue in result["issues"]:
                    st.warning(issue)

else:
    st.info("👆 Upload medical documents and ask a question to begin.")