#!/usr/bin/env python3
"""
MCP City Desk Agent - Streamlit Dashboard
KPI-first control room for municipal AI operations
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="MCP City Desk Agent",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .error-metric {
        border-left-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏛️ MCP City Desk Agent</h1>
    <p>AI-Powered Municipal Data Intelligence & Research Automation</p>
</div>
""", unsafe_allow_html=True)

# ---- Navigation (modern st.Page API) ----
overview = st.Page("pages/01_overview.py", title="Overview", icon="🏠")
search = st.Page("pages/02_rag_search.py", title="RAG Search", icon="🔎")
docs = st.Page("pages/03_collections.py", title="Collections", icon="📚")
costs = st.Page("pages/04_costs_rates.py", title="Costs & Rate Limits", icon="💸")
logs = st.Page("pages/05_logs.py", title="Logs", icon="📓")

# Navigation bar
nav = st.navigation([overview, search, docs, costs, logs])

# Run the selected page
nav.run()
