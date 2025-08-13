"""
RAG Search Page - Query Interface
Interactive search with your MCP-RAG-LLM pipeline
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
import json
from pathlib import Path

from lib.clients import (
    execute_rag_query,
    execute_llm_synthesis,
    get_available_providers,
    log_query_metrics
)

st.title("🔎 RAG Search")
st.markdown("**Query NYC Agency Documents with AI-Powered Intelligence**")

# Sidebar configuration
with st.sidebar:
    st.subheader("🔧 Search Configuration")
    
    # Query input
    query = st.text_input(
        "Ask a question",
        value=st.query_params.get("q", ""),
        placeholder="e.g., What are the building permit requirements?",
        help="Enter your municipal government question"
    )
    
    # Model selection
    providers = get_available_providers()
    if providers:
        provider = st.selectbox(
            "LLM Provider",
            providers,
            index=providers.index("google_gemini") if "google_gemini" in providers else 0,
            help="Choose the AI model for synthesis"
        )
    else:
        st.error("No LLM providers available")
        provider = None
    
    # Top-K selection
    top_k = st.slider(
        "Top-K Results",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of document chunks to retrieve"
    )
    
    # Search button
    search_button = st.button(
        "🚀 Search & Synthesize",
        type="primary",
        use_container_width=True,
        disabled=not provider
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        st.checkbox("Show raw chunks", value=False, key="show_raw")
        st.checkbox("Enable cost tracking", value=True, key="track_costs")
        st.checkbox("Detailed timing", value=True, key="detailed_timing")

# Main search interface
if search_button and query.strip():
    # Update URL for shareable links
    st.query_params["q"] = query
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: RAG Retrieval
        status_text.text("🔍 Retrieving relevant documents...")
        progress_bar.progress(25)
        
        # Execute RAG query
        rag_result = asyncio.run(execute_rag_query(query, top_k))
        
        if not rag_result["success"]:
            st.error(f"RAG retrieval failed: {rag_result.get('error')}")
            st.stop()
        
        progress_bar.progress(50)
        status_text.text("🧠 Synthesizing answer with AI...")
        
        # Step 2: LLM Synthesis
        llm_result = asyncio.run(execute_llm_synthesis(
            query, 
            rag_result["results"], 
            provider
        ))
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Display results
        st.success("Search completed successfully!")
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Documents Found",
                rag_result["results_count"],
                help="Number of relevant document chunks"
            )
        
        with col2:
            st.metric(
                "Retrieval Time",
                f"{rag_result['retrieval_time']:.2f}s",
                help="Time to find relevant documents"
            )
        
        with col3:
            if llm_result["success"]:
                st.metric(
                    "Synthesis Time",
                    f"{llm_result['synthesis_time']:.2f}s",
                    help="Time for AI to generate answer"
                )
            else:
                st.metric("Synthesis Time", "Failed")
        
        with col4:
            if llm_result["success"]:
                total_time = rag_result['retrieval_time'] + llm_result['synthesis_time']
                st.metric(
                    "Total Time",
                    f"{total_time:.2f}s",
                    help="End-to-end query time"
                )
            else:
                st.metric("Total Time", "N/A")
        
        # AI-Generated Answer
        st.subheader("🤖 AI-Generated Answer")
        
        if llm_result["success"]:
            # Display the answer
            st.markdown(llm_result["response"])
            
            # Answer metadata
            answer_col1, answer_col2, answer_col3 = st.columns(3)
            
            with answer_col1:
                st.info(f"**Provider:** {llm_result['provider']}")
            
            with answer_col2:
                st.info(f"**Model:** {llm_result['model']}")
            
            with answer_col3:
                st.info(f"**Tokens Used:** {llm_result['tokens_used']}")
            
            # Copyable citation block
            st.subheader("📋 Citation Block")
            citation_text = f"""
**Query:** {query}

**Answer:** {llm_result['response'][:200]}...

**Sources:** {rag_result['results_count']} document chunks from NYC agency PDFs
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model:** {llm_result['provider']} ({llm_result['model']})
            """.strip()
            
            st.code(citation_text, language="markdown")
            
            # Download citation
            st.download_button(
                label="📥 Download Citation",
                data=citation_text,
                file_name=f"citation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
        else:
            st.error(f"LLM synthesis failed: {llm_result.get('error')}")
            st.warning("Showing RAG results only")
        
        # Document Sources
        st.subheader("📚 Source Documents")
        
        for i, doc in enumerate(rag_result["results"]):
            with st.expander(f"📄 Source {i+1} - {doc.get('metadata', {}).get('filename', 'Unknown')}"):
                # Document metadata
                meta = doc.get('metadata', {})
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**File:** {meta.get('filename', 'Unknown')}")
                    st.write(f"**Page:** {meta.get('page', 'N/A')}")
                    st.write(f"**Source:** {meta.get('source', 'Unknown')}")
                
                with col2:
                    if 'ingested_at' in meta:
                        st.write(f"**Ingested:** {meta['ingested_at']}")
                    if 'filesize_bytes' in meta:
                        st.write(f"**Size:** {meta['filesize_bytes']:,} bytes")
                
                # Document content
                st.markdown("**Content Preview:**")
                content = doc.get('document_text', '')
                
                if st.session_state.get("show_raw", False):
                    st.code(content, language="text")
                else:
                    # Show formatted preview
                    preview_length = 800
                    if len(content) > preview_length:
                        st.markdown(content[:preview_length] + "...")
                        st.caption(f"Showing first {preview_length} characters. Enable 'Show raw chunks' for full content.")
                    else:
                        st.markdown(content)
                
                # Relevance score
                if 'relevance_score' in doc:
                    score = doc['relevance_score']
                    if score > 0.1:
                        st.success(f"Relevance: {score:.3f} (High)")
                    elif score > -0.1:
                        st.info(f"Relevance: {score:.3f} (Medium)")
                    else:
                        st.warning(f"Relevance: {score:.3f} (Low)")
        
        # Log metrics for cost tracking
        if st.session_state.get("track_costs", True) and llm_result["success"]:
            log_query_metrics(
                query=query,
                success=True,
                retrieval_time=rag_result['retrieval_time'],
                synthesis_time=llm_result['synthesis_time'],
                tokens_used=llm_result['tokens_used'],
                provider=provider
            )
        
        # Performance insights
        if st.session_state.get("detailed_timing", True):
            st.subheader("⚡ Performance Insights")
            
            # Timing breakdown
            timing_data = {
                "Phase": ["Document Retrieval", "AI Synthesis", "Total"],
                "Time (s)": [
                    rag_result['retrieval_time'],
                    llm_result['synthesis_time'] if llm_result["success"] else 0,
                    rag_result['retrieval_time'] + (llm_result['synthesis_time'] if llm_result["success"] else 0)
                ]
            }
            
            import pandas as pd
            timing_df = pd.DataFrame(timing_data)
            st.dataframe(timing_df, use_container_width=True)
            
            # Performance analysis
            if rag_result['retrieval_time'] < 0.5:
                st.success("🚀 Fast retrieval - Excellent vector search performance")
            elif rag_result['retrieval_time'] < 1.0:
                st.info("⚡ Good retrieval - Acceptable performance")
            else:
                st.warning("🐌 Slow retrieval - Consider optimizing vector search")
            
            if llm_result["success"]:
                if llm_result['synthesis_time'] < 3.0:
                    st.success("🚀 Fast synthesis - LLM responding quickly")
                elif llm_result['synthesis_time'] < 8.0:
                    st.info("⚡ Good synthesis - Normal LLM response time")
                else:
                    st.warning("🐌 Slow synthesis - LLM may be experiencing delays")
        
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        st.exception(e)
    
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()

else:
    # Welcome message and example queries
    st.info("👆 Use the sidebar to configure your search and click 'Search & Synthesize'")
    
    # Example queries
    st.subheader("💡 Example Queries")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("""
        **Building & Permits:**
        - What are the building permit requirements?
        - How do I apply for a construction permit?
        - What inspections are required for renovations?
        
        **Business & Licensing:**
        - How do I apply for a business license?
        - What are the requirements for food service?
        - How do I renew my vendor permit?
        """)
    
    with example_col2:
        st.markdown("""
        **Health & Safety:**
        - What are the health standards for restaurants?
        - How do I report a code violation?
        - What are the safety requirements for events?
        
        **General Information:**
        - What services does this agency provide?
        - How do I contact the department?
        - What are the office hours?
        """)
    
    # Recent searches (if available)
    try:
        metrics_file = Path("./query_metrics.jsonl")
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                lines = f.readlines()
                if lines:
                    st.subheader("🕒 Recent Searches")
                    
                    # Get last 5 unique queries
                    recent_queries = []
                    seen_queries = set()
                    
                    for line in reversed(lines):
                        if len(recent_queries) >= 5:
                            break
                        try:
                            data = json.loads(line.strip())
                            query_text = data.get('query', '')
                            if query_text and query_text not in seen_queries:
                                recent_queries.append(data)
                                seen_queries.add(query_text)
                        except:
                            continue
                    
                    if recent_queries:
                        for query_data in recent_queries:
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(query_data['query'])
                            with col2:
                                status = "✅" if query_data['success'] else "❌"
                                st.write(status)
                            with col3:
                                st.write(f"{query_data['total_time']:.1f}s")
                    else:
                        st.info("No recent searches found")
    except:
        pass

# Footer
st.markdown("---")
st.caption("💡 **Pro Tip:** Use specific, detailed questions for better results. The AI will search through 1,000+ NYC agency document chunks to find the most relevant information.")
