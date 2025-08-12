import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from .chromadb_manager import ChromaDBManager
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class RAGQueryEngine:
    """RAG query engine for intelligent document retrieval and response generation"""
    
    def __init__(self, chroma_manager: ChromaDBManager, 
                 document_processor: DocumentProcessor):
        self.chroma_manager = chroma_manager
        self.document_processor = document_processor
    
    def is_healthy(self) -> bool:
        """Check if the RAG engine is healthy"""
        return self.chroma_manager.is_healthy()
    
    async def ingest_pdf(self, file_path: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest a PDF file into the RAG system"""
        start_time = time.time()
        
        try:
            # Process the PDF
            documents = self.document_processor.process_pdf(file_path, metadata)
            if not documents:
                return {
                    "success": False,
                    "error": "No documents extracted from PDF",
                    "file_path": file_path
                }
            
            # Add to ChromaDB
            success = self.chroma_manager.add_documents(documents)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to add documents to vector database",
                    "file_path": file_path
                }
            
            # Get processing stats
            stats = self.document_processor.get_processing_stats(documents)
            execution_time = int((time.time() - start_time) * 1000)
            
            result = {
                "success": True,
                "file_path": file_path,
                "documents_created": len(documents),
                "processing_stats": stats,
                "execution_time_ms": execution_time,
                "ingested_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully ingested PDF {file_path}: {len(documents)} chunks in {execution_time}ms")
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"PDF ingestion failed for {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "execution_time_ms": execution_time
            }
    
    async def ingest_directory(self, directory_path: str, 
                              file_pattern: str = "*.pdf",
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest all PDF files in a directory"""
        start_time = time.time()
        
        try:
            # Process all PDFs in directory
            documents = self.document_processor.process_directory(
                directory_path, file_pattern, metadata
            )
            
            if not documents:
                return {
                    "success": False,
                    "error": f"No PDF files found in {directory_path}",
                    "directory_path": directory_path
                }
            
            # Add to ChromaDB
            success = self.chroma_manager.add_documents(documents)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to add documents to vector database",
                    "directory_path": directory_path
                }
            
            # Get processing stats
            stats = self.document_processor.get_processing_stats(documents)
            execution_time = int((time.time() - start_time) * 1000)
            
            result = {
                "success": True,
                "directory_path": directory_path,
                "documents_created": len(documents),
                "processing_stats": stats,
                "execution_time_ms": execution_time,
                "ingested_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully ingested directory {directory_path}: {len(documents)} chunks in {execution_time}ms")
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Directory ingestion failed for {directory_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "directory_path": directory_path,
                "execution_time_ms": execution_time
            }
    
    async def query_documents(self, query: str, 
                             n_results: int = 5,
                             filter_metadata: Optional[Dict[str, Any]] = None,
                             include_context: bool = True) -> Dict[str, Any]:
        """Query documents using RAG approach"""
        start_time = time.time()
        
        try:
            if not query.strip():
                return {
                    "success": False,
                    "error": "Empty query provided",
                    "query": query
                }
            
            # Search for relevant documents
            search_results = self.chroma_manager.search_documents(
                query, n_results, filter_metadata
            )
            
            if not search_results:
                return {
                    "success": False,
                    "error": "No relevant documents found",
                    "query": query,
                    "n_results": n_results
                }
            
            # Prepare response
            execution_time = int((time.time() - start_time) * 1000)
            
            response = {
                "success": True,
                "query": query,
                "results_count": len(search_results),
                "execution_time_ms": execution_time,
                "queried_at": datetime.utcnow().isoformat(),
                "results": []
            }
            
            # Format results
            for result in search_results:
                formatted_result = {
                    "document_id": result.get("id"),
                    "relevance_score": 1.0 - (result.get("distance", 0) if result.get("distance") else 0),
                    "metadata": result.get("metadata", {})
                }
                
                if include_context:
                    formatted_result["document_text"] = result.get("document", "")
                
                response["results"].append(formatted_result)
            
            logger.info(f"RAG query '{query}' returned {len(search_results)} results in {execution_time}ms")
            return response
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"RAG query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "execution_time_ms": execution_time
            }
    
    async def hybrid_query(self, query: str, 
                          n_results: int = 5,
                          filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform hybrid query combining RAG with structured data"""
        start_time = time.time()
        
        try:
            # First, get RAG results
            rag_results = await self.query_documents(
                query, n_results, filter_metadata, include_context=True
            )
            
            if not rag_results["success"]:
                return rag_results
            
            # TODO: In the future, this could combine with:
            # - Structured database queries
            # - API data from external sources
            # - Real-time data feeds
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # For now, return RAG results with hybrid flag
            hybrid_response = rag_results.copy()
            hybrid_response["query_type"] = "hybrid"
            hybrid_response["execution_time_ms"] = execution_time
            hybrid_response["data_sources"] = ["document_rag"]
            
            logger.info(f"Hybrid query '{query}' completed in {execution_time}ms")
            return hybrid_response
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Hybrid query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "execution_time_ms": execution_time
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            chroma_stats = self.chroma_manager.get_collection_stats()
            
            return {
                "rag_engine": {
                    "status": "healthy" if self.is_healthy() else "unhealthy",
                    "chroma_db": chroma_stats
                },
                "document_processor": {
                    "chunk_size": self.document_processor.chunk_size,
                    "chunk_overlap": self.document_processor.chunk_overlap
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {"error": str(e)}
    
    def reset_system(self) -> Dict[str, Any]:
        """Reset the RAG system (use with caution)"""
        try:
            success = self.chroma_manager.reset_collection()
            
            return {
                "success": success,
                "message": "RAG system reset successfully" if success else "Failed to reset RAG system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to reset RAG system: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
