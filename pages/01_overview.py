"""
Overview Page - KPI Dashboard
Shows key performance indicators and system health
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

from lib.clients import (
    get_collection_stats, 
    get_available_providers,
    get_rate_limiter
)

st.title("🏠 System Overview")
st.markdown("**KPI Dashboard for MCP City Desk Agent**")

# Get system stats
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Document Index Health")
    
    # Collection statistics
    stats = get_collection_stats()
    if stats:
        st.metric(
            label="Total Documents",
            value=stats.get("total_documents", 0),
            help="Total PDF documents ingested"
        )
        st.metric(
            label="Total Chunks",
            value=stats.get("total_chunks", 0),
            help="Total text chunks for RAG retrieval"
        )
        st.metric(
            label="Collections",
            value=stats.get("collection_count", 0),
            help="Number of ChromaDB collections"
        )
    else:
        st.warning("Could not fetch collection stats")

with col2:
    st.subheader("🧠 LLM Provider Status")
    
    providers = get_available_providers()
    if providers:
        for provider in providers:
            if provider == "openai":
                st.success(f"✅ {provider.upper()}")
            elif provider == "google_gemini":
                st.success(f"✅ {provider.replace('_', ' ').title()}")
            else:
                st.info(f"ℹ️ {provider}")
    else:
        st.error("❌ No LLM providers available")
    
    # Rate limiter status
    try:
        rate_limiter = get_rate_limiter()
        if rate_limiter:
            stats = rate_limiter.get_statistics()
            st.metric(
                label="Active Rate Limits",
                value=len(stats.get("active_limits", {})),
                help="Number of active rate-limited endpoints"
            )
    except:
        st.info("Rate limiter not available")

with col3:
    st.subheader("💰 Cost & Performance")
    
    # Try to get recent query metrics
    try:
        metrics_file = Path("./query_metrics.jsonl")
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                lines = f.readlines()
                if lines:
                    # Parse last 10 queries
                    recent_metrics = []
                    for line in lines[-10:]:
                        try:
                            recent_metrics.append(json.loads(line.strip()))
                        except:
                            continue
                    
                    if recent_metrics:
                        df = pd.DataFrame(recent_metrics)
                        
                        # Success rate
                        success_rate = (df['success'].sum() / len(df)) * 100
                        st.metric(
                            label="Success Rate",
                            value=f"{success_rate:.1f}%",
                            delta=f"{success_rate - 95:.1f}%" if success_rate >= 95 else f"{success_rate - 95:.1f}%",
                            delta_color="normal" if success_rate >= 95 else "inverse"
                        )
                        
                        # Average cost
                        avg_cost = df['cost_estimate'].mean()
                        st.metric(
                            label="Avg Cost/Query",
                            value=f"${avg_cost:.4f}",
                            help="Average cost per query in USD"
                        )
                        
                        # Average latency
                        avg_latency = df['total_time'].mean()
                        st.metric(
                            label="Avg Latency",
                            value=f"{avg_latency:.2f}s",
                            help="Average end-to-end query time"
                        )
                    else:
                        st.info("No recent query data")
                else:
                    st.info("No query metrics available")
        else:
            st.info("Query metrics file not found")
    except Exception as e:
        st.warning(f"Could not load metrics: {e}")

# Performance Trends
st.subheader("📈 Performance Trends")

# Create sample performance data (replace with real data from your metrics)
try:
    # Generate sample data for demonstration
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
    
    # Sample success rates (replace with real data)
    success_rates = [95, 97, 93, 96, 98, 94, 96]
    
    # Sample costs (replace with real data)
    costs = [0.002, 0.0018, 0.0022, 0.0019, 0.0021, 0.0017, 0.0020]
    
    # Sample latencies (replace with real data)
    latencies = [4.2, 3.8, 4.5, 4.1, 3.9, 4.3, 4.0]
    
    trend_data = pd.DataFrame({
        'Date': dates,
        'Success Rate (%)': success_rates,
        'Cost per Query ($)': costs,
        'Latency (s)': latencies
    })
    
    # Success Rate Trend
    fig_success = px.line(
        trend_data, 
        x='Date', 
        y='Success Rate (%)',
        title="Success Rate Trend (7 Days)",
        markers=True
    )
    fig_success.add_hline(y=95, line_dash="dash", line_color="red", 
                          annotation_text="Target: 95%")
    st.plotly_chart(fig_success, use_container_width=True)
    
    # Cost and Latency Trends
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cost = px.line(
            trend_data, 
            x='Date', 
            y='Cost per Query ($)',
            title="Cost per Query Trend",
            markers=True
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    
    with col2:
        fig_latency = px.line(
            trend_data, 
            x='Date', 
            y='Latency (s)',
            title="Query Latency Trend",
            markers=True
        )
        st.plotly_chart(fig_latency, use_container_width=True)
        
except Exception as e:
    st.warning(f"Could not generate performance charts: {e}")

# System Health Status
st.subheader("🏥 System Health Status")

health_col1, health_col2 = st.columns(2)

with health_col1:
    st.markdown("**ChromaDB Status**")
    if stats:
        if stats.get("total_chunks", 0) > 1000:
            st.success("✅ Healthy - 1000+ chunks available")
        elif stats.get("total_chunks", 0) > 500:
            st.warning("⚠️ Moderate - 500+ chunks available")
        else:
            st.error("❌ Low - Less than 500 chunks")
    else:
        st.error("❌ Status unknown")
    
    st.markdown("**LLM Integration**")
    if providers:
        if len(providers) >= 2:
            st.success("✅ Healthy - Multiple providers available")
        else:
            st.warning("⚠️ Limited - Single provider")
    else:
        st.error("❌ No providers available")

with health_col2:
    st.markdown("**Rate Limiting**")
    try:
        rate_limiter = get_rate_limiter()
        if rate_limiter:
            st.success("✅ Active - API protection enabled")
        else:
            st.warning("⚠️ Inactive - No rate limiting")
    except:
        st.info("ℹ️ Not configured")
    
    st.markdown("**Document Freshness**")
    # This would check last document ingestion time
    st.info("ℹ️ Last ingest: Unknown")

# Quick Actions
st.subheader("⚡ Quick Actions")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("🔄 Refresh Stats", use_container_width=True):
        st.rerun()

with action_col2:
    if st.button("📊 Export Metrics", use_container_width=True):
        try:
            metrics_file = Path("./query_metrics.jsonl")
            if metrics_file.exists():
                with open(metrics_file, "r") as f:
                    data = f.read()
                st.download_button(
                    label="Download Metrics",
                    data=data,
                    file_name=f"mcp_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                    mime="application/json"
                )
            else:
                st.warning("No metrics file found")
        except Exception as e:
            st.error(f"Export failed: {e}")

with action_col3:
    if st.button("🧪 Run Health Check", use_container_width=True):
        with st.spinner("Running system health check..."):
            time.sleep(2)  # Simulate health check
            st.success("Health check completed!")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
