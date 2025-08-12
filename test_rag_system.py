#!/usr/bin/env python3
"""
Test script for RAG Layer with ChromaDB
"""

import asyncio
import json
from pathlib import Path
from src.mcp_server.rag.chromadb_manager import ChromaDBManager
from src.mcp_server.rag.document_processor import DocumentProcessor
from src.mcp_server.rag.query_engine import RAGQueryEngine

async def test_rag_components():
    """Test individual RAG components"""
    print("Testing RAG Components...")
    print("=" * 40)
    
    # Test ChromaDB Manager
    print("\n1. Testing ChromaDB Manager...")
    try:
        chroma_manager = ChromaDBManager("./test_chroma_db")
        is_healthy = chroma_manager.is_healthy()
        print(f"   ChromaDB healthy: {is_healthy}")
        
        if is_healthy:
            stats = chroma_manager.get_collection_stats()
            print(f"   Collection stats: {stats}")
    except Exception as e:
        print(f"   ChromaDB test failed: {e}")
    
    # Test Document Processor
    print("\n2. Testing Document Processor...")
    try:
        doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        print(f"   Chunk size: {doc_processor.chunk_size}")
        print(f"   Chunk overlap: {doc_processor.chunk_overlap}")
        
        # Test with sample text (since we don't have PDFs yet)
        sample_text = "This is a sample municipal document about city regulations. It contains important information about zoning laws and building codes that city officials need to know."
        chunks = doc_processor._chunk_text(sample_text)
        print(f"   Sample text chunked into {len(chunks)} pieces")
        
    except Exception as e:
        print(f"   Document processor test failed: {e}")
    
    # Test RAG Query Engine
    print("\n3. Testing RAG Query Engine...")
    try:
        if 'chroma_manager' in locals() and 'doc_processor' in locals():
            rag_engine = RAGQueryEngine(chroma_manager, doc_processor)
            is_healthy = rag_engine.is_healthy()
            print(f"   RAG Engine healthy: {is_healthy}")
            
            if is_healthy:
                stats = rag_engine.get_system_stats()
                print(f"   System stats: {json.dumps(stats, indent=2)}")
        else:
            print("   Skipping RAG Engine test - dependencies not available")
            
    except Exception as e:
        print(f"   RAG Engine test failed: {e}")

async def test_document_ingestion():
    """Test document ingestion workflow"""
    print("\n\nTesting Document Ingestion...")
    print("=" * 40)
    
    try:
        # Create test components
        chroma_manager = ChromaDBManager("./test_chroma_db")
        doc_processor = DocumentProcessor()
        rag_engine = RAGQueryEngine(chroma_manager, doc_processor)
        
        # Create a test text file to simulate PDF content
        test_file = "test_document.txt"
        test_content = """
        Municipal Code Section 101: Building Permits
        
        All construction projects within city limits must obtain proper building permits.
        Applications must be submitted to the Department of Building and Safety.
        Processing time is typically 5-10 business days.
        
        Section 102: Zoning Requirements
        
        Residential zones allow single-family homes and duplexes.
        Commercial zones permit retail, office, and light industrial use.
        Mixed-use zones combine residential and commercial development.
        
        Section 103: Environmental Compliance
        
        All projects must comply with environmental impact regulations.
        Stormwater management systems are required for projects over 5000 sq ft.
        Energy efficiency standards apply to all new construction.
        """
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"   Created test document: {test_file}")
        
        # Simulate PDF processing (we'll use the text content directly)
        documents = doc_processor._chunk_text(test_content)
        print(f"   Document chunked into {len(documents)} pieces")
        
        # Add to ChromaDB
        success = chroma_manager.add_documents([
            {
                "id": f"test_doc_chunk_{i}",
                "text": chunk,
                "metadata": {
                    "source": "test_document.txt",
                    "chunk_index": i,
                    "document_type": "municipal_code"
                }
            }
            for i, chunk in enumerate(documents)
        ])
        
        print(f"   Documents added to ChromaDB: {success}")
        
        # Clean up test file
        Path(test_file).unlink()
        print(f"   Cleaned up test file")
        
    except Exception as e:
        print(f"   Document ingestion test failed: {e}")

async def test_rag_queries():
    """Test RAG query functionality"""
    print("\n\nTesting RAG Queries...")
    print("=" * 40)
    
    try:
        chroma_manager = ChromaDBManager("./test_chroma_db")
        doc_processor = DocumentProcessor()
        rag_engine = RAGQueryEngine(chroma_manager, doc_processor)
        
        # Test queries
        test_queries = [
            "building permit requirements",
            "zoning regulations for commercial use",
            "environmental compliance standards",
            "stormwater management requirements"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                result = await rag_engine.query_documents(query, n_results=3)
                if result["success"]:
                    print(f"   Results: {result['results_count']} documents found")
                    for i, doc in enumerate(result["results"][:2]):  # Show first 2 results
                        print(f"     {i+1}. Score: {doc['relevance_score']:.3f}")
                        if "document_text" in doc:
                            text_preview = doc["document_text"][:100] + "..."
                            print(f"        Preview: {text_preview}")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"   Query failed: {e}")
        
    except Exception as e:
        print(f"   RAG query test failed: {e}")

async def main():
    """Run all RAG tests"""
    print("MCP City Desk Agent - RAG System Test Suite")
    print("=" * 50)
    
    await test_rag_components()
    await test_document_ingestion()
    await test_rag_queries()
    
    print("\n" + "=" * 50)
    print("RAG System Test Suite Completed!")
    print("\nNext steps:")
    print("1. Test with actual PDF documents")
    print("2. Verify ChromaDB persistence")
    print("3. Test hybrid queries with external data")

if __name__ == "__main__":
    asyncio.run(main())
