"""
Logs Page - Activity and Improvements Tracking
Live view of system logs and improvement management
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

st.title("📓 System Logs & Improvements")
st.markdown("**Activity Tracking and Improvement Management**")

# Load log files
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_activity_log():
    """Load activity log from markdown file"""
    try:
        log_file = Path("./activity_log.md")
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "No activity log found"
    except Exception as e:
        return f"Error loading activity log: {e}"

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_improvements():
    """Load improvements from markdown file"""
    try:
        improvements_file = Path("./improvements.md")
        if improvements_file.exists():
            with open(improvements_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "No improvements file found"
    except Exception as e:
        return f"Error loading improvements: {e}"

# Load logs
activity_log = load_activity_log()
improvements = load_improvements()

# Activity Log
st.subheader("📝 Activity Log")
st.markdown("**Chronological audit trail of decisions and changes**")

# Activity log controls
log_col1, log_col2, log_col3 = st.columns([2, 1, 1])

with log_col1:
    log_search = st.text_input(
        "Search activity log",
        placeholder="Search for specific activities, dates, or keywords",
        help="Filter activity log entries"
    )

with log_col2:
    log_filter = st.selectbox(
        "Filter by",
        ["All", "Today", "This Week", "This Month"],
        help="Filter by time period"
    )

with log_col3:
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Display activity log
if log_search:
    # Simple search highlighting
    if log_search.lower() in activity_log.lower():
        st.success(f"✅ Found '{log_search}' in activity log")
        # Highlight search term (simple approach)
        highlighted_log = activity_log.replace(
            log_search, f"**{log_search}**"
        )
        st.markdown(highlighted_log)
    else:
        st.warning(f"❌ No entries found for '{log_search}'")
        st.markdown(activity_log)
else:
    st.markdown(activity_log)

# Improvements Management
st.subheader("🚀 Improvements & Backlog")
st.markdown("**Feature requests, bugs, and enhancement tracking**")

# Improvements controls
imp_col1, imp_col2 = st.columns([3, 1])

with imp_col1:
    imp_search = st.text_input(
        "Search improvements",
        placeholder="Search for specific improvements or categories",
        help="Filter improvement entries"
    )

with imp_col2:
    if st.button("🔄 Refresh Improvements", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Display improvements
if imp_search:
    if imp_search.lower() in improvements.lower():
        st.success(f"✅ Found '{imp_search}' in improvements")
        highlighted_improvements = improvements.replace(
            imp_search, f"**{imp_search}**"
        )
        st.markdown(highlighted_improvements)
    else:
        st.warning(f"❌ No improvements found for '{imp_search}'")
        st.markdown(improvements)
else:
    st.markdown(improvements)

# Add New Improvement
st.subheader("➕ Add New Improvement")

with st.form("new_improvement"):
    st.markdown("**Submit a new improvement, bug report, or feature request**")
    
    # Improvement details
    improvement_title = st.text_input(
        "Title",
        placeholder="Brief description of the improvement",
        help="Clear, concise title for the improvement"
    )
    
    improvement_type = st.selectbox(
        "Type",
        ["Feature Request", "Bug Fix", "Enhancement", "Documentation", "Performance", "Security"],
        help="Category of the improvement"
    )
    
    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High", "Critical"],
        help="Priority level for implementation"
    )
    
    effort = st.selectbox(
        "Effort Estimate",
        ["Small (1-2 days)", "Medium (1-2 weeks)", "Large (1+ months)"],
        help="Estimated effort to implement"
    )
    
    description = st.text_area(
        "Description",
        placeholder="Detailed description of the improvement, including:\n- What needs to be improved\n- Why it's important\n- How it should work\n- Any constraints or considerations",
        height=150,
        help="Comprehensive description of the improvement"
    )
    
    expected_impact = st.text_area(
        "Expected Impact",
        placeholder="How will this improvement affect:\n- User experience\n- System performance\n- KPI metrics\n- Development workflow",
        height=100,
        help="Expected benefits and impact"
    )
    
    # Submit button
    submitted = st.form_submit_button("📝 Submit Improvement", type="primary")
    
    if submitted:
        if improvement_title and description:
            try:
                # Format the improvement entry
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                improvement_entry = f"""
## [{improvement_type}] {improvement_title}

**Priority:** {priority}  
**Effort:** {effort}  
**Submitted:** {timestamp}  
**Status:** [ ] Pending

### Description
{description}

### Expected Impact
{expected_impact}

### Notes
- [ ] Requirements gathering
- [ ] Design review
- [ ] Implementation
- [ ] Testing
- [ ] Documentation
- [ ] Deployment

---

"""
                
                # Append to improvements file
                improvements_file = Path("./improvements.md")
                
                if improvements_file.exists():
                    with open(improvements_file, "a", encoding="utf-8") as f:
                        f.write(improvement_entry)
                else:
                    # Create new file if it doesn't exist
                    with open(improvements_file, "w", encoding="utf-8") as f:
                        f.write(f"# Improvements & Backlog\n\n{improvement_entry}")
                
                st.success("✅ Improvement submitted successfully!")
                st.info("The improvement has been added to improvements.md")
                
                # Clear form
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to submit improvement: {e}")
        else:
            st.error("❌ Please fill in both title and description")

# Quick Actions
st.subheader("⚡ Quick Actions")

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📊 Export Activity Log", use_container_width=True):
        try:
            st.download_button(
                label="Download Activity Log",
                data=activity_log,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Export failed: {e}")

with action_col2:
    if st.button("📊 Export Improvements", use_container_width=True):
        try:
            st.download_button(
                label="Download Improvements",
                data=improvements,
                file_name=f"improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Export failed: {e}")

with action_col3:
    if st.button("🧹 Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Cache cleared!")

# Log Statistics
st.subheader("📈 Log Statistics")

try:
    # Parse activity log for statistics
    activity_lines = activity_log.split('\n')
    
    # Count entries by date
    date_counts = {}
    for line in activity_lines:
        if line.startswith('## '):
            # Extract date from activity log entries
            if ' – ' in line:
                date_part = line.split(' – ')[0]
                if date_part.startswith('## '):
                    date = date_part[3:].strip()
                    date_counts[date] = date_counts.get(date, 0) + 1
    
    if date_counts:
        # Create date distribution chart
        import plotly.express as px
        
        dates = list(date_counts.keys())
        counts = list(date_counts.values())
        
        fig = px.bar(
            x=dates,
            y=counts,
            title="Activity Log Entries by Date",
            labels={'x': 'Date', 'y': 'Number of Entries'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entries", sum(counts))
        
        with col2:
            st.metric("Active Days", len(dates))
        
        with col3:
            avg_entries = sum(counts) / len(dates) if dates else 0
            st.metric("Avg Entries/Day", f"{avg_entries:.1f}")
    
    # Parse improvements for statistics
    improvement_lines = improvements.split('\n')
    
    # Count improvements by type and status
    improvement_types = {}
    pending_count = 0
    completed_count = 0
    
    for line in improvement_lines:
        if line.startswith('## ['):
            # Extract type
            if ']' in line:
                imp_type = line.split('[')[1].split(']')[0]
                improvement_types[imp_type] = improvement_types.get(imp_type, 0) + 1
        
        if '**Status:** [ ] Pending' in line:
            pending_count += 1
        elif '**Status:** [x] Completed' in line:
            completed_count += 1
    
    if improvement_types:
        # Improvement type distribution
        imp_col1, imp_col2 = st.columns(2)
        
        with imp_col1:
            st.markdown("**📊 Improvement Types**")
            for imp_type, count in improvement_types.items():
                st.write(f"- {imp_type}: {count}")
        
        with imp_col2:
            st.markdown("**📋 Status Summary**")
            st.metric("Pending", pending_count)
            st.metric("Completed", completed_count)
            if pending_count + completed_count > 0:
                completion_rate = (completed_count / (pending_count + completed_count)) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")

except Exception as e:
    st.warning(f"Could not generate statistics: {e}")

# Recent Activity Summary
st.subheader("🕒 Recent Activity Summary")

try:
    # Show last 5 activity log entries
    activity_entries = []
    current_entry = ""
    
    for line in activity_lines:
        if line.startswith('## '):
            if current_entry:
                activity_entries.append(current_entry.strip())
            current_entry = line
        else:
            current_entry += line + "\n"
    
    if current_entry:
        activity_entries.append(current_entry.strip())
    
    # Show recent entries
    recent_entries = activity_entries[-5:] if len(activity_entries) > 5 else activity_entries
    
    if recent_entries:
        for entry in recent_entries:
            with st.expander(entry.split('\n')[0][3:], expanded=False):
                st.markdown(entry)
    else:
        st.info("No recent activity entries found")

except Exception as e:
    st.warning(f"Could not load recent activity: {e}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
