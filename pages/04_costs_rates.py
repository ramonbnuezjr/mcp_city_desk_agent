"""
Costs & Rate Limits Page - Financial and API Monitoring
Track costs, usage, and rate limiting across all providers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

from lib.clients import get_rate_limiter, get_cost_estimate

st.title("💸 Costs & Rate Limits")
st.markdown("**Financial Tracking and API Usage Monitoring**")

# Load query metrics
@st.cache_data(ttl=60)
def load_query_metrics():
    """Load and parse query metrics from JSONL file"""
    try:
        metrics_file = Path("./query_metrics.jsonl")
        if not metrics_file.exists():
            return pd.DataFrame()
        
        metrics = []
        with open(metrics_file, "r") as f:
            for line in f:
                try:
                    metrics.append(json.loads(line.strip()))
                except:
                    continue
        
        if metrics:
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df['date'] = df['timestamp'].dt.date
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.warning(f"Could not load metrics: {e}")
        return pd.DataFrame()

# Load metrics
metrics_df = load_query_metrics()

# Cost Overview
st.subheader("💰 Cost Overview")

if not metrics_df.empty:
    # Calculate costs by provider
    cost_by_provider = metrics_df.groupby('provider')['cost_estimate'].agg(['sum', 'mean', 'count']).round(6)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_cost = metrics_df['cost_estimate'].sum()
        st.metric(
            "Total Cost",
            f"${total_cost:.6f}",
            help="Total cost across all queries"
        )
    
    with col2:
        total_queries = len(metrics_df)
        st.metric(
            "Total Queries",
            total_queries,
            help="Total number of queries executed"
        )
    
    with col3:
        avg_cost_per_query = metrics_df['cost_estimate'].mean()
        st.metric(
            "Avg Cost/Query",
            f"${avg_cost_per_query:.6f}",
            help="Average cost per query"
        )
    
    # Cost breakdown by provider
    st.subheader("📊 Cost Breakdown by Provider")
    
    if len(cost_by_provider) > 0:
        provider_col1, provider_col2 = st.columns(2)
        
        with provider_col1:
            # Cost summary table
            st.markdown("**Cost Summary by Provider**")
            cost_summary = cost_by_provider.copy()
            cost_summary.columns = ['Total Cost ($)', 'Avg Cost/Query ($)', 'Query Count']
            st.dataframe(cost_summary, use_container_width=True)
        
        with provider_col2:
            # Cost pie chart
            fig_pie = px.pie(
                values=cost_by_provider['sum'],
                names=cost_by_provider.index,
                title="Cost Distribution by Provider"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Daily cost trends
    st.subheader("📈 Daily Cost Trends")
    
    if len(metrics_df) > 1:
        daily_costs = metrics_df.groupby('date')['cost_estimate'].sum().reset_index()
        daily_costs['date'] = pd.to_datetime(daily_costs['date'])
        
        fig_daily = px.line(
            daily_costs,
            x='date',
            y='cost_estimate',
            title="Daily Cost Trends",
            markers=True
        )
        fig_daily.update_layout(yaxis_title="Cost ($)")
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Cost vs performance
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost vs latency scatter
            fig_scatter = px.scatter(
                metrics_df,
                x='total_time',
                y='cost_estimate',
                color='provider',
                title="Cost vs Latency",
                labels={'total_time': 'Total Time (s)', 'cost_estimate': 'Cost ($)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Cost efficiency by provider
            efficiency_data = metrics_df.groupby('provider').agg({
                'cost_estimate': 'sum',
                'tokens_used': 'sum'
            }).reset_index()
            efficiency_data['cost_per_token'] = efficiency_data['cost_estimate'] / efficiency_data['tokens_used']
            
            fig_efficiency = px.bar(
                efficiency_data,
                x='provider',
                y='cost_per_token',
                title="Cost per Token by Provider",
                labels={'cost_per_token': 'Cost per Token ($)'}
            )
            st.plotly_chart(fig_efficiency, use_container_width=True)
    
else:
    st.info("📊 No query metrics available yet. Run some searches to see cost data!")

# Rate Limiting Status
st.subheader("🚦 Rate Limiting Status")

try:
    rate_limiter = get_rate_limiter()
    if rate_limiter:
        stats = rate_limiter.get_statistics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            active_limits = len(stats.get("active_limits", {}))
            st.metric(
                "Active Rate Limits",
                active_limits,
                help="Number of endpoints currently rate-limited"
            )
        
        with col2:
            total_requests = stats.get("total_requests", 0)
            st.metric(
                "Total Requests",
                total_requests,
                help="Total requests processed"
            )
        
        with col3:
            blocked_requests = stats.get("blocked_requests", 0)
            st.metric(
                "Blocked Requests",
                blocked_requests,
                help="Requests blocked due to rate limits"
            )
        
        # Rate limit details
        if active_limits > 0:
            st.markdown("**📋 Active Rate Limits:**")
            
            for endpoint, limit_info in stats.get("active_limits", {}).items():
                with st.expander(f"🔒 {endpoint}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Limit:** {limit_info.get('limit', 'Unknown')}")
                        st.write(f"**Window:** {limit_info.get('window', 'Unknown')}s")
                    
                    with col2:
                        st.write(f"**Current:** {limit_info.get('current', 'Unknown')}")
                        st.write(f"**Remaining:** {limit_info.get('remaining', 'Unknown')}")
                    
                    with col3:
                        st.write(f"**Blocked:** {limit_info.get('blocked', 'Unknown')}")
                        st.write(f"**Reset:** {limit_info.get('reset_time', 'Unknown')}")
        
        # Rate limit statistics
        if total_requests > 0:
            st.markdown("**📊 Rate Limiting Statistics:**")
            
            # Success vs blocked rate
            success_rate = ((total_requests - blocked_requests) / total_requests) * 100
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Request Success Rate (%)"},
                delta={'reference': 95},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 80], 'color': "lightgray"},
                        {'range': [80, 95], 'color': "yellow"},
                        {'range': [95, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    else:
        st.warning("⚠️ Rate limiter not available")
        
except Exception as e:
    st.info(f"ℹ️ Rate limiting information not available: {e}")

# API Usage Monitoring
st.subheader("📡 API Usage Monitoring")

# Provider status
st.markdown("**🔌 Provider Status**")

providers = ["openai", "google_gemini", "nyc_open_data", "weather_api"]

provider_col1, provider_col2 = st.columns(2)

with provider_col1:
    for provider in providers[:2]:
        if provider == "openai":
            st.info("🔵 **OpenAI API**")
            st.write("Status: Active")
            st.write("Model: gpt-4o-mini")
            st.write("Rate Limit: 3,000 RPM")
        elif provider == "google_gemini":
            st.success("🟢 **Google Gemini API**")
            st.write("Status: Active")
            st.write("Model: gemini-2.0-flash-exp")
            st.write("Rate Limit: 15 QPS")

with provider_col2:
    for provider in providers[2:]:
        if provider == "nyc_open_data":
            st.info("🔵 **NYC Open Data API**")
            st.write("Status: Active")
            st.write("Rate Limit: 1,000 requests/hour")
        elif provider == "weather_api":
            st.info("🔵 **OpenWeatherMap API**")
            st.write("Status: Active")
            st.write("Rate Limit: 60 calls/minute")

# Usage patterns
if not metrics_df.empty:
    st.subheader("📊 Usage Patterns")
    
    # Queries by time of day
    metrics_df['hour'] = metrics_df['timestamp'].dt.hour
    hourly_usage = metrics_df.groupby('hour').size().reset_index(name='queries')
    
    fig_hourly = px.bar(
        hourly_usage,
        x='hour',
        y='queries',
        title="Query Volume by Hour of Day",
        labels={'hour': 'Hour (24h)', 'queries': 'Number of Queries'}
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Provider usage over time
    provider_usage = metrics_df.groupby(['date', 'provider']).size().reset_index(name='queries')
    provider_usage['date'] = pd.to_datetime(provider_usage['date'])
    
    fig_provider = px.line(
        provider_usage,
        x='date',
        y='queries',
        color='provider',
        title="Provider Usage Over Time",
        labels={'date': 'Date', 'queries': 'Number of Queries'}
    )
    st.plotly_chart(fig_provider, use_container_width=True)

# Budget Management
st.subheader("💳 Budget Management")

budget_col1, budget_col2 = st.columns(2)

with budget_col1:
    st.markdown("**💰 Set Budget Limits**")
    
    monthly_budget = st.number_input(
        "Monthly Budget ($)",
        min_value=0.0,
        max_value=1000.0,
        value=50.0,
        step=5.0,
        help="Set monthly spending limit"
    )
    
    if st.button("💾 Save Budget", use_container_width=True):
        st.success(f"Budget set to ${monthly_budget}/month")
    
    # Budget tracking
    if not metrics_df.empty:
        current_month = datetime.now().month
        month_metrics = metrics_df[metrics_df['timestamp'].dt.month == current_month]
        month_cost = month_metrics['cost_estimate'].sum()
        
        budget_used = (month_cost / monthly_budget) * 100 if monthly_budget > 0 else 0
        
        st.metric(
            "Month-to-Date Spending",
            f"${month_cost:.6f}",
            delta=f"{budget_used:.1f}% of budget"
        )
        
        # Budget progress bar
        st.progress(min(budget_used / 100, 1.0))
        
        if budget_used > 90:
            st.warning("⚠️ Approaching budget limit!")
        elif budget_used > 75:
            st.info("ℹ️ Budget usage is moderate")

with budget_col2:
    st.markdown("**📈 Cost Projections**")
    
    if not metrics_df.empty:
        # Calculate daily average cost
        daily_avg = metrics_df.groupby('date')['cost_estimate'].sum().mean()
        monthly_projection = daily_avg * 30
        
        st.metric(
            "Projected Monthly Cost",
            f"${monthly_projection:.6f}",
            help="Based on current usage patterns"
        )
        
        # Cost savings recommendations
        st.markdown("**💡 Cost Optimization Tips:**")
        
        if len(metrics_df) > 5:
            # Analyze provider costs
            provider_costs = metrics_df.groupby('provider')['cost_estimate'].mean()
            cheapest_provider = provider_costs.idxmin()
            most_expensive = provider_costs.idxmax()
            
            if cheapest_provider != most_expensive:
                savings = provider_costs[most_expensive] - provider_costs[cheapest_provider]
                st.info(f"💡 Use {cheapest_provider} more to save ${savings:.6f} per query")
        
        st.info("💡 Batch similar queries to reduce API calls")
        st.info("💡 Use appropriate model sizes for complexity")
        st.info("💡 Monitor and adjust rate limits")

# Export and Reports
st.subheader("📊 Export & Reports")

export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("📥 Export Cost Data", use_container_width=True):
        if not metrics_df.empty:
            csv_data = metrics_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"cost_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to export")

with export_col2:
    if st.button("📋 Generate Cost Report", use_container_width=True):
        if not metrics_df.empty:
            # Generate a simple cost report
            report = f"""
# MCP City Desk Agent - Cost Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Queries: {len(metrics_df)}
- Total Cost: ${metrics_df['cost_estimate'].sum():.6f}
- Average Cost per Query: ${metrics_df['cost_estimate'].mean():.6f}

## By Provider
{metrics_df.groupby('provider')['cost_estimate'].agg(['sum', 'mean', 'count']).to_string()}

## Daily Breakdown
{metrics_df.groupby('date')['cost_estimate'].sum().to_string()}
            """.strip()
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        else:
            st.warning("No data for report generation")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
