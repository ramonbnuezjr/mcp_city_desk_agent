"""
Collections Page - Document Browser
Browse and manage your NYC agency document collection
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import subprocess
import sys

from lib.clients import get_chroma_manager, get_collection_stats

st.title("📚 Document Collections")
st.markdown("**Browse and Manage NYC Agency PDF Collection**")

# Get collection information
stats = get_collection_stats()
chroma_manager = get_chroma_manager()

if not chroma_manager:
    st.error("❌ ChromaDB manager not available")
    st.stop()

# Collection overview
st.subheader("📊 Collection Overview")

if stats:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Documents",
            stats.get("total_documents", 0),
            help="Number of unique PDF files"
        )
    
    with col2:
        st.metric(
            "Total Chunks",
            stats.get("total_chunks", 0),
            help="Number of text chunks for RAG"
        )
    
    with col3:
        st.metric(
            "Collections",
            stats.get("collection_count", 0),
            help="Number of ChromaDB collections"
        )
    
    with col4:
        avg_chunks = stats.get("total_chunks", 0) / max(stats.get("total_documents", 1), 1)
        st.metric(
            "Avg Chunks/Doc",
            f"{avg_chunks:.1f}",
            help="Average chunks per document"
        )
else:
    st.warning("Could not fetch collection statistics")

# Document browser
st.subheader("🔍 Document Browser")

# Search and filter options
search_col1, search_col2, search_col3 = st.columns([2, 1, 1])

with search_col1:
    search_term = st.text_input(
        "Search documents",
        placeholder="Enter filename, agency, or content keywords",
        help="Search through document metadata and content"
    )

with search_col2:
    agency_filter = st.selectbox(
        "Filter by Agency",
        ["All", "TLC", "DOHMH", "OTI", "DSS-DHS", "Other"],
        help="Filter documents by NYC agency"
    )

with search_col3:
    sort_by = st.selectbox(
        "Sort by",
        ["Filename", "Size", "Ingested Date", "Chunk Count"],
        help="Sort documents by different criteria"
    )

# Try to get document list
try:
    # This would need to be implemented in your ChromaDB manager
    # For now, we'll show a placeholder
    st.info("📋 Document browsing functionality requires additional ChromaDB methods")
    
    # Placeholder document data
    sample_docs = [
        {
            "filename": "NYC - TLC Rule Book Chapter 59.pdf",
            "agency": "TLC",
            "size_mb": 2.4,
            "chunks": 45,
            "ingested": "2025-01-27",
            "status": "✅ Active"
        },
        {
            "filename": "NYC - DOHMH Standards of Conduct 2024.pdf",
            "agency": "DOHMH",
            "size_mb": 1.8,
            "chunks": 32,
            "ingested": "2025-01-27",
            "status": "✅ Active"
        },
        {
            "filename": "NYC - OTI Artificial Intelligence Governance Audit.pdf",
            "agency": "OTI",
            "size_mb": 3.2,
            "chunks": 67,
            "ingested": "2025-01-27",
            "status": "✅ Active"
        },
        {
            "filename": "NYC - DSS-DHS Fiscal Manual.pdf",
            "agency": "DSS-DHS",
            "size_mb": 4.1,
            "chunks": 89,
            "ingested": "2025-01-27",
            "status": "✅ Active"
        }
    ]
    
    # Filter documents
    if search_term:
        sample_docs = [doc for doc in sample_docs if search_term.lower() in doc["filename"].lower()]
    
    if agency_filter != "All":
        sample_docs = [doc for doc in sample_docs if doc["agency"] == agency_filter]
    
    # Sort documents
    if sort_by == "Filename":
        sample_docs.sort(key=lambda x: x["filename"])
    elif sort_by == "Size":
        sample_docs.sort(key=lambda x: x["size_mb"], reverse=True)
    elif sort_by == "Ingested Date":
        sample_docs.sort(key=lambda x: x["ingested"], reverse=True)
    elif sort_by == "Chunk Count":
        sample_docs.sort(key=lambda x: x["chunks"], reverse=True)
    
    # Display documents
    if sample_docs:
        st.markdown(f"**Found {len(sample_docs)} documents**")
        
        for doc in sample_docs:
            with st.expander(f"📄 {doc['filename']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Agency:** {doc['agency']}")
                    st.write(f"**Size:** {doc['size_mb']} MB")
                
                with col2:
                    st.write(f"**Chunks:** {doc['chunks']}")
                    st.write(f"**Status:** {doc['status']}")
                
                with col3:
                    st.write(f"**Ingested:** {doc['ingested']}")
                    
                    # Action buttons
                    if st.button(f"🔍 View Chunks", key=f"view_{doc['filename']}"):
                        st.info(f"Viewing chunks for {doc['filename']}")
                        # This would show the actual chunks from ChromaDB
                    
                    if st.button(f"📊 Analyze", key=f"analyze_{doc['filename']}"):
                        st.info(f"Analyzing {doc['filename']}")
                        # This would show document analysis
                
                # Document preview (placeholder)
                st.markdown("**Content Preview:**")
                st.info("Document content preview would be displayed here")
                
    else:
        st.warning("No documents found matching your criteria")

except Exception as e:
    st.error(f"Error browsing documents: {e}")

# Document management
st.subheader("⚙️ Document Management")

management_col1, management_col2 = st.columns(2)

with management_col1:
    st.markdown("**📥 Re-ingest Documents**")
    
    if st.button("🔄 Re-ingest All PDFs", use_container_width=True):
        with st.spinner("Re-ingesting all PDFs..."):
            try:
                # Run the ingestion script
                result = subprocess.run([
                    sys.executable, "ingest_nyc_pdfs.py"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    st.success("✅ Re-ingestion completed successfully!")
                    st.info("Refresh the page to see updated statistics")
                else:
                    st.error(f"❌ Re-ingestion failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                st.error("❌ Re-ingestion timed out (5 minutes)")
            except Exception as e:
                st.error(f"❌ Re-ingestion error: {e}")
    
    st.markdown("**📁 Add New Documents**")
    
    uploaded_files = st.file_uploader(
        "Upload new PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload additional NYC agency PDFs"
    )
    
    if uploaded_files:
        st.info(f"📤 {len(uploaded_files)} files selected for upload")
        
        if st.button("🚀 Process Uploaded Files", use_container_width=True):
            st.warning("File upload processing not yet implemented")
            st.info("For now, place PDFs in data/nyc_agency_pdfs/ and use re-ingest")

with management_col2:
    st.markdown("**🧹 Collection Maintenance**")
    
    if st.button("🧹 Clean Orphaned Chunks", use_container_width=True):
        st.info("Cleanup functionality not yet implemented")
    
    if st.button("📊 Rebuild Index", use_container_width=True):
        st.info("Index rebuild functionality not yet implemented")
    
    if st.button("🗑️ Delete Collection", use_container_width=True, type="secondary"):
        if st.checkbox("I understand this will delete all documents"):
            st.error("Delete functionality not yet implemented")
    
    st.markdown("**📈 Analytics**")
    
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Report generation not yet implemented")

# Collection health
st.subheader("🏥 Collection Health")

health_col1, health_col2 = st.columns(2)

with health_col1:
    st.markdown("**📊 Chunk Distribution**")
    
    if stats and stats.get("total_chunks", 0) > 0:
        # Simple chunk distribution chart
        import plotly.express as px
        
        # Sample chunk distribution by document
        chunk_data = {
            "Document": [f"Doc {i+1}" for i in range(min(8, stats.get("total_documents", 0)))],
            "Chunks": [stats.get("total_chunks", 0) // max(stats.get("total_documents", 1), 1)] * min(8, stats.get("total_documents", 0))
        }
        
        fig = px.bar(
            chunk_data,
            x="Document",
            y="Chunks",
            title="Chunk Distribution by Document"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No chunk data available for visualization")

with health_col2:
    st.markdown("**🔍 Quality Metrics**")
    
    if stats:
        total_chunks = stats.get("total_chunks", 0)
        total_docs = stats.get("total_documents", 0)
        
        if total_docs > 0:
            avg_chunks = total_chunks / total_docs
            
            # Quality indicators
            if avg_chunks >= 100:
                st.success("✅ Excellent chunk density")
            elif avg_chunks >= 50:
                st.info("⚡ Good chunk density")
            elif avg_chunks >= 20:
                st.warning("⚠️ Moderate chunk density")
            else:
                st.error("❌ Low chunk density")
            
            st.metric("Average Chunks/Document", f"{avg_chunks:.1f}")
            
            # Coverage estimate
            estimated_pages = total_chunks * 2  # Rough estimate
            st.metric("Estimated Pages Covered", f"{estimated_pages:,}")
        else:
            st.warning("No documents available")
    else:
        st.warning("Collection statistics not available")

# Recent activity
st.subheader("🕒 Recent Activity")

try:
    # Check for recent ingestion logs
    log_file = Path("./ingestion_log.txt")
    if log_file.exists():
        with open(log_file, "r") as f:
            lines = f.readlines()
            if lines:
                st.markdown("**📝 Latest Ingestion Logs:**")
                for line in lines[-5:]:  # Show last 5 lines
                    st.code(line.strip())
            else:
                st.info("No recent ingestion activity")
    else:
        st.info("No ingestion logs found")
        
except Exception as e:
    st.warning(f"Could not load activity logs: {e}")

# Footer
st.markdown("---")
st.caption(f"Collection last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
