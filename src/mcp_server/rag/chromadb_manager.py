import chromadb
import logging
from typing import List, Dict, Any, Optional
from chromadb.config import Settings
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ChromaDBManager:
    """Manages ChromaDB operations for document storage and retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._init_client()
    
    def _init_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="municipal_documents",
                metadata={
                    "description": "Municipal documents and regulations for RAG queries",
                    "source": "MCP City Desk Agent"
                }
            )
            
            logger.info(f"ChromaDB initialized successfully at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def is_healthy(self) -> bool:
        """Check if ChromaDB is healthy"""
        try:
            if self.client and self.collection:
                # Simple health check by getting collection info
                info = self.collection.get()
                return True
            return False
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector database"""
        try:
            if not documents:
                logger.warning("No documents provided for ingestion")
                return False
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get("id", f"doc_{len(ids)}")
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                
                if text.strip():  # Only add non-empty documents
                    ids.append(doc_id)
                    texts.append(text)
                    metadatas.append(metadata)
            
            if ids:
                # Add to collection
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Successfully added {len(ids)} documents to ChromaDB")
                return True
            else:
                logger.warning("No valid documents found for ingestion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5, 
                        filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity"""
        try:
            if not query.strip():
                logger.warning("Empty query provided")
                return []
            
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "document": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                        "id": results["ids"][0][i] if results["ids"] else None
                    })
            
            logger.info(f"Search query '{query}' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            if not self.collection:
                return {"error": "Collection not initialized"}
            
            # Get collection info
            info = self.collection.get()
            count = len(info["ids"]) if info["ids"] else 0
            
            return {
                "total_documents": count,
                "collection_name": "municipal_documents",
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete specific documents from the collection"""
        try:
            if not document_ids:
                return False
            
            self.collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)"""
        try:
            if self.collection:
                self.client.delete_collection("municipal_documents")
                self.collection = self.client.create_collection("municipal_documents")
                logger.info("Collection reset successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False
