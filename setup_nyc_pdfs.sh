#!/bin/bash

echo "NYC Agency PDF Setup Script"
echo "=========================="

# Create necessary directories
echo "Creating directories..."
mkdir -p data/nyc_agency_pdfs
mkdir -p data/embeddings_cache

echo "✅ Directories created:"
echo "   - data/nyc_agency_pdfs/ (for your PDF files)"
echo "   - data/embeddings_cache/ (for embeddings)"

echo ""
echo "📁 Next steps:"
echo "1. Copy your 8 NYC agency PDFs to: data/nyc_agency_pdfs/"
echo "2. Run: python ingest_nyc_pdfs.py"
echo "3. Your PDFs will be processed and added to the RAG system"
echo ""
echo "💡 Tip: You can also use the MCP Server endpoints to query the ingested documents"
