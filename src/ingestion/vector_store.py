import chromadb
from sentence_transformers import SentenceTransformer
import os

class MedicalVectorStore:
    def __init__(self, persist_dir="./data/chroma_db"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="medical_docs",
            metadata={"hnsw:space": "cosine"}
        )
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_document(self, chunks: list, metadata: dict) -> int:
        """Add document chunks to vector store"""
        if not chunks:
            return 0
        
        embeddings = self.encoder.encode(chunks).tolist()
        source = metadata.get("source", "unknown")
        
        ids = [f"{source}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{**metadata, "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list:
        """Search for relevant chunks"""
        query_embedding = self.encoder.encode([query]).tolist()
        
        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            chunks = []
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    similarity = 1 - distance
                    chunks.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "similarity": round(similarity, 3)
                    })
            
            return chunks
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_stats(self) -> dict:
        """Get collection statistics"""
        count = self.collection.count()
        return {"total_chunks": count}