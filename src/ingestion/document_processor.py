import pdfplumber
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )

    def process_pdf(self, pdf_path: str) -> dict:
        """Extract text from medical PDF"""
        text = ""
        metadata = {
            "source": os.path.basename(pdf_path),
            "type": "pdf",
            "pages": 0
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata["pages"] = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {page_num + 1}]\n{page_text}"
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            return None
        
        if not text.strip():
            return None
        
        # Create chunks
        chunks = self.splitter.split_text(text)
        
        return {
            "text": text,
            "chunks": chunks,
            "metadata": metadata
        }

    def process_txt(self, txt_path: str) -> dict:
        """Extract text from TXT file"""
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        chunks = self.splitter.split_text(text)
        
        return {
            "text": text,
            "chunks": chunks,
            "metadata": {
                "source": os.path.basename(txt_path),
                "type": "txt"
            }
        }

    def process(self, file_path: str) -> dict:
        """Route to correct processor"""
        if file_path.lower().endswith(".pdf"):
            return self.process_pdf(file_path)
        elif file_path.lower().endswith(".txt"):
            return self.process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")