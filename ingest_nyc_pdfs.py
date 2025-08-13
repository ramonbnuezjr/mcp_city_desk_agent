#!/usr/bin/env python3
"""
NYC Agency PDF Ingestion Script
Ingests real NYC agency PDFs into the RAG system for realistic testing
"""

import asyncio
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
from src.mcp_server.rag.chromadb_manager import ChromaDBManager
from src.mcp_server.rag.document_processor import DocumentProcessor
from src.mcp_server.rag.query_engine import RAGQueryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
    logger.warning("pypdf not available. Install pypdf>=4.2.0")

class NYC_PDF_Ingester:
    """Handles ingestion of NYC agency PDFs into the RAG system"""
    
    def __init__(self):
        self.pdf_dir = Path("./data/nyc_agency_pdfs")
        self.embeddings_dir = Path("./data/embeddings_cache")
        self.chroma_db_path = "./nyc_agency_chroma_db"
        
        # Initialize RAG components
        self.chroma_manager = ChromaDBManager(self.chroma_db_path)
        self.doc_processor = DocumentProcessor()
        self.rag_engine = RAGQueryEngine(self.chroma_manager, self.doc_processor)
        
        # NYC agency categories for better organization
        self.agency_categories = {
            "building": ["building", "construction", "permit", "code", "safety"],
            "zoning": ["zoning", "planning", "land_use", "development"],
            "environmental": ["environmental", "sustainability", "climate", "green"],
            "transportation": ["transportation", "traffic", "parking", "transit"],
            "public_safety": ["police", "fire", "emergency", "safety"],
            "health": ["health", "sanitation", "food", "medical"],
            "education": ["education", "school", "university", "learning"],
            "finance": ["finance", "budget", "tax", "revenue"]
        }
    
    def _sanitize_metadata(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chroma metadata must be str|int|float|bool|None.
        Convert common Python types (Path, datetime, lists/sets/tuples, dicts) to strings.
        """
        out = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                out[k] = v
            elif isinstance(v, Path):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            elif isinstance(v, (list, tuple, set)):
                out[k] = ", ".join(map(str, v))
            else:
                out[k] = str(v)
        return out
    
    def extract_pdf_text(self, pdf_path: Path) -> List[str]:
        """
        Lightweight text extractor via pypdf with AES support (requires cryptography).
        Falls back to skipping if encrypted and cannot be opened.
        """
        if PdfReader is None:
            raise RuntimeError("pypdf not available. Install pypdf>=4.2.0")
        
        try:
            reader = PdfReader(str(pdf_path))
            
            # Handle encrypted PDFs
            if getattr(reader, "is_encrypted", False):
                try:
                    # Try empty password first (common for 'encrypted but not password-protected' PDFs)
                    reader.decrypt("")
                    logger.info(f"Successfully decrypted encrypted PDF: {pdf_path.name}")
                except Exception as e:
                    logger.warning(f"Could not decrypt PDF {pdf_path.name}: {e}")
                    raise RuntimeError(f"Encrypted PDF needs crypto backend: {e}")
            
            texts = []
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    if text.strip():  # Only add non-empty pages
                        texts.append(text)
                except Exception as e:
                    logger.warning(f"Page {i+1} extraction failed in {pdf_path.name}: {e}")
                    texts.append("")
            
            return texts
            
        except Exception as e:
            logger.error(f"PDF text extraction failed for {pdf_path}: {e}")
            raise RuntimeError(f"PDF processing error: {e}")
    
    def get_pdf_files(self) -> list:
        """Get list of available PDF files"""
        if not self.pdf_dir.exists():
            print(f"❌ PDF directory not found: {self.pdf_dir}")
            return []
        
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        print(f"📁 Found {len(pdf_files)} PDF files in {self.pdf_dir}")
        
        for pdf_file in pdf_files:
            file_size = pdf_file.stat().st_size / (1024 * 1024)  # MB
            print(f"   📄 {pdf_file.name} ({file_size:.1f} MB)")
        
        return pdf_files
    
    def categorize_pdf(self, filename: str) -> str:
        """Automatically categorize PDF based on filename and content"""
        filename_lower = filename.lower()
        
        # Check filename for obvious categories
        for category, keywords in self.agency_categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return category
        
        # Default to "general" if no clear category
        return "general"
    
    async def ingest_single_pdf(self, pdf_path: Path) -> dict:
        """Ingest a single PDF file"""
        try:
            print(f"\n🔄 Processing: {pdf_path.name}")
            
            # Extract text from PDF
            try:
                texts = self.extract_pdf_text(pdf_path)
                if not texts:
                    print(f"   ⚠️  No text extracted from {pdf_path.name}")
                    return {"success": False, "file": pdf_path.name, "error": "No text extracted"}
                
                print(f"   📄 Extracted {len(texts)} pages from {pdf_path.name}")
                
            except RuntimeError as e:
                print(f"   ❌ Text extraction failed for {pdf_path.name}: {e}")
                return {"success": False, "file": pdf_path.name, "error": str(e)}
            
            # Process text chunks
            try:
                # Use document processor to chunk the text
                all_text = "\n\n".join(texts)
                chunks = self.doc_processor._chunk_text(all_text)
                
                print(f"   ✂️  Created {len(chunks)} text chunks")
                
                # Prepare documents for ChromaDB
                documents = []
                for i, chunk in enumerate(chunks):
                    if chunk.strip():  # Skip empty chunks
                        documents.append({
                            "id": f"{pdf_path.stem}_chunk_{i}",
                            "text": chunk,
                            "metadata": self._sanitize_metadata({
                                "source": "nyc_agency",
                                "filename": pdf_path.name,
                                "agency_category": self.categorize_pdf(pdf_path.name),
                                "ingestion_date": datetime.utcnow().isoformat(),
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "file_size_bytes": pdf_path.stat().st_size,
                                "document_type": "pdf"
                            })
                        })
                
                # Add to ChromaDB
                success = self.chroma_manager.add_documents(documents)
                
                if success:
                    print(f"   ✅ Successfully ingested {pdf_path.name}")
                    print(f"      Chunks created: {len(chunks)}")
                    print(f"      Category: {self.categorize_pdf(pdf_path.name)}")
                    return {"success": True, "file": pdf_path.name, "chunks_created": len(chunks)}
                else:
                    print(f"   ❌ Failed to add documents to ChromaDB for {pdf_path.name}")
                    return {"success": False, "file": pdf_path.name, "error": "ChromaDB add failed"}
                    
            except Exception as e:
                print(f"   ❌ Processing failed for {pdf_path.name}: {e}")
                return {"success": False, "file": pdf_path.name, "error": str(e)}
                
        except Exception as e:
            print(f"   ❌ Error processing {pdf_path.name}: {e}")
            return {"success": False, "file": pdf_path.name, "error": str(e)}
    
    async def ingest_all_pdfs(self) -> dict:
        """Ingest all available PDFs"""
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            return {"success": False, "error": "No PDF files found"}
        
        print(f"\n🚀 Starting ingestion of {len(pdf_files)} PDF files...")
        
        results = []
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            result = await self.ingest_single_pdf(pdf_file)
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        # Summary
        print(f"\n📊 Ingestion Summary:")
        print(f"   Total files: {len(pdf_files)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        return {
            "success": failed == 0,
            "total_files": len(pdf_files),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    async def test_rag_queries(self):
        """Test RAG system with ingested documents"""
        print(f"\n🧪 Testing RAG queries with ingested documents...")
        
        # Get collection stats
        stats = self.chroma_manager.get_collection_stats()
        print(f"   Documents in collection: {stats.get('total_documents', 0)}")
        
        # Test queries
        test_queries = [
            "What are the building permit requirements?",
            "What zoning regulations apply to residential areas?",
            "What environmental standards must be met?",
            "How do I apply for a business license?",
            "What are the safety requirements for construction projects?"
        ]
        
        for query in test_queries:
            print(f"\n   🔍 Query: '{query}'")
            try:
                result = await self.rag_engine.query_documents(query, n_results=3)
                if result["success"]:
                    print(f"      Results: {result['results_count']} documents found")
                    for i, doc in enumerate(result["results"][:2]):
                        print(f"        {i+1}. Score: {doc['relevance_score']:.3f}")
                        if "document_text" in doc:
                            text_preview = doc["document_text"][:80] + "..."
                            print(f"           Preview: {text_preview}")
                else:
                    print(f"      Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"      Query failed: {e}")
    
    def get_ingestion_status(self) -> dict:
        """Get current status of ingested documents"""
        try:
            stats = self.chroma_manager.get_collection_stats()
            pdf_files = self.get_pdf_files()
            
            return {
                "pdf_directory": str(self.pdf_dir),
                "available_pdfs": len(pdf_files),
                "ingested_documents": stats.get('total_documents', 0),
                "chroma_db_path": self.chroma_db_path,
                "embeddings_directory": str(self.embeddings_dir)
            }
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Main ingestion process"""
    print("NYC Agency PDF Ingestion Script")
    print("=" * 50)
    
    # Initialize ingester
    ingester = NYC_PDF_Ingester()
    
    # Check current status
    status = ingester.get_ingestion_status()
    print(f"📊 Current Status:")
    print(f"   PDF Directory: {status['pdf_directory']}")
    print(f"   Available PDFs: {status['available_pdfs']}")
    print(f"   Ingested Documents: {status['ingested_documents']}")
    
    if status['available_pdfs'] == 0:
        print(f"\n⚠️  No PDF files found in {status['pdf_directory']}")
        print(f"   Please copy your NYC agency PDFs to this directory and run again.")
        return
    
    # Ask user if they want to proceed
    print(f"\n🚀 Ready to ingest {status['available_pdfs']} PDF files.")
    print(f"   This will create embeddings and add them to the RAG system.")
    
    # Ingest all PDFs
    ingestion_result = await ingester.ingest_all_pdfs()
    
    if ingestion_result["success"]:
        print(f"\n🎉 All PDFs ingested successfully!")
        
        # Test the RAG system
        await ingester.test_rag_queries()
        
        print(f"\n✅ NYC Agency PDFs are now available for RAG queries!")
        print(f"   You can use the MCP Server endpoints to query this data.")
        
    else:
        print(f"\n⚠️  Some PDFs failed to ingest. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
