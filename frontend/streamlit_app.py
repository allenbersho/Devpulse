import streamlit as st
import httpx
import json
import re
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="DevPulse | Enterprise-Grade GitHub Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    /* Gradient Header */
    .title-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sleek Cards */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #2a5298;
    }
    
    .metric-lbl {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #6c757d;
        letter-spacing: 1px;
    }
    
    /* Agent Badge */
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    .badge-repo_info { background-color: #e3f2fd; color: #0d47a1; }
    .badge-issue_triage { background-color: #fbe9e7; color: #d84315; }
    .badge-release_notes { background-color: #e8f5e9; color: #1b5e20; }
    .badge-analytics { background-color: #f3e5f5; color: #4a148c; }
    .badge-security { background-color: #efebe9; color: #4e342e; }
    .badge-documentation { background-color: #efebe9; color: #37474f; }
    
    /* Chat Bubble styling */
    .chat-bubble {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        max-width: 80%;
    }
    
    .user-bubble {
        background-color: #e3f2fd;
        margin-left: auto;
        color: #0d47a1;
        border-bottom-right-radius: 0;
    }
    
    .assistant-bubble {
        background-color: #f1f3f4;
        margin-right: auto;
        color: #202124;
        border-bottom-left-radius: 0;
    }
</style>
""", unsafe_allow_html=True)

# API Endpoint URL
API_URL = "http://localhost:8000"

# Sidebar settings
st.sidebar.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=80)
st.sidebar.markdown("# DevPulse Control Panel")
st.sidebar.markdown("---")

session_id = st.sidebar.text_input("Session ID", value="default-session", help="Conversations are saved by Session ID in SQLite")

# Check API backend connection
backend_running = False
try:
    r = httpx.get(API_URL, timeout=2)
    if r.status_code == 200:
        backend_running = True
except Exception:
    pass

if backend_running:
    st.sidebar.success("🟢 API Server Connected")
else:
    st.sidebar.error("🔴 API Server Offline")
    st.sidebar.warning("Run `uvicorn api.app:app --port 8000` to start backend.")

# Retrieve environment variable states via backend or direct check
github_token_set = os.environ.get("GITHUB_TOKEN") is not None
if github_token_set:
    st.sidebar.info("🔑 GITHUB_TOKEN Configured (5,000 req/hr)")
else:
    st.sidebar.warning("⚠️ No GITHUB_TOKEN (60 req/hr rate limit)")

# Reset conversation
if st.sidebar.button("🗑️ Clear Conversation Memory", use_container_width=True):
    if backend_running:
        try:
            httpx.post(f"{API_URL}/clear", json={"session_id": session_id})
            st.sidebar.success("Memory reset successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error resetting memory: {e}")
    else:
        st.sidebar.error("Cannot clear memory: backend offline.")

# Main layout
st.markdown("""
<div class="title-container">
    <h1>⚡ DevPulse Platform</h1>
    <p>Enterprise-Grade Multi-Agent GitHub Intelligence & Compliance Auditing Platform</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Live Chat Agent",
    "📊 Repository Explorer",
    "⚖️ Side-by-Side Comparer",
    "🔍 Agent Discovery (A2A)"
])

# ==================== TAB 1: Chat Agent ====================
with tab1:
    st.markdown("### Conversational Assistant")
    st.caption("Ask questions about any repository. DevPulse dynamically detects the repository name and routes queries to specialized agents.")
    
    # Session state to store messages locally to show in chat layout
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Print chat history
    for msg in st.session_state["messages"]:
        role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        badge_html = ""
        if msg["role"] == "assistant" and "category" in msg and msg["category"]:
            badge_html = f'<div class="agent-badge badge-{msg["category"]}">🤖 {msg["category"].upper()} AGENT</div><br>'
            
        st.markdown(f"""
        <div class="chat-bubble {role_class}">
            {badge_html}
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Print tool logs if any
        if msg["role"] == "assistant" and "tools" in msg and msg["tools"]:
            with st.expander("🛠️ Executed Tools Log", expanded=False):
                for tool in msg["tools"]:
                    st.code(f"Tool: {tool['tool']}\nResult: {tool['result'][:250]}...")

    # Chat Input
    query_input = st.chat_input("Ask DevPulse (e.g. 'Tell me about facebook/react' or 'Give me the health score for vuejs/core')")
    
    if query_input:
        # Show user message immediately
        st.session_state["messages"].append({"role": "user", "content": query_input})
        st.rerun()

    # If there is a new user message, trigger request
    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        user_query = st.session_state["messages"][-1]["content"]
        
        if backend_running:
            with st.spinner("DevPulse agents are reasoning..."):
                try:
                    res = httpx.post(
                        f"{API_URL}/chat",
                        json={"session_id": session_id, "query": user_query},
                        timeout=60
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": data["answer"],
                            "category": data["category"],
                            "tools": data["tool_calls"]
                        })
                        st.rerun()
                    else:
                        st.error(f"Backend API returned error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Connection failure to backend API: {e}")
        else:
            st.error("API Server offline. Please start the backend and try again.")

# ==================== TAB 2: Repository Explorer ====================
with tab2:
    st.markdown("### Repository Deep-Dive Analysis")
    st.caption("Perform complete health, contributor, security, and documentation auditing on any public repository.")

    col1, col2 = st.columns([3, 1])
    with col1:
        repo_name_input = st.text_input("Repository Name (Format: owner/repo)", value="facebook/react")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("Run Analytics Audit", use_container_width=True)

    if analyze_btn:
        if "/" not in repo_name_input:
            st.error("Invalid format. Repository must be in the format 'owner/repo' (e.g. facebook/react)")
        elif not backend_running:
            st.error("Backend API is offline.")
        else:
            owner, repo = repo_name_input.split("/", 1)
            
            with st.spinner(f"Analyzing {owner}/{repo}..."):
                try:
                    # 1. Health Score Report
                    health_res = httpx.post(f"{API_URL}/health", json={"owner": owner, "repo": repo})
                    
                    # 2. Issues Audit / Contributor audit via direct chat or mock calls
                    # We can use API chat queries for specific insights to build a visual panel
                    st.markdown("---")
                    st.subheader(f"📊 Audit Results: {repo_name_input}")
                    
                    if health_res.status_code == 200:
                        report_text = health_res.json()["report"]
                        
                        # Extract Score from report
                        score_match = re.search(r"Overall Health Score:\s*(\d+)/100", report_text)
                        grade_match = re.search(r"Rating Grade:\s*(.+)", report_text)
                        
                        score_val = int(score_match.group(1)) if score_match else 50
                        grade_val = grade_match.group(1) if grade_match else "C"
                        
                        # Draw metric columns
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-lbl">Overall Health Score</div>
                                <div class="metric-val">{score_val}/100</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with m2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-lbl">Project Rating</div>
                                <div class="metric-val">{grade_val}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with m3:
                            # Run quick check on issues
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-lbl">Audited Date</div>
                                <div class="metric-val">{datetime.utcnow().strftime('%Y-%m-%d')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        # Show raw reports
                        st.markdown("### Health Score Breakdown")
                        st.markdown(report_text)
                    else:
                        st.error("Failed to retrieve health scorecard.")
                        
                    # 3. Pull additional reports (Security and Documentation audits)
                    st.markdown("---")
                    st.markdown("### 🛡️ Compliance Audits")
                    
                    sec_res = httpx.post(f"{API_URL}/chat", json={
                        "session_id": "audit-temp",
                        "query": f"Run a security audit for {repo_name_input}"
                    }, timeout=30)
                    doc_res = httpx.post(f"{API_URL}/chat", json={
                        "session_id": "audit-temp",
                        "query": f"Run a documentation audit for {repo_name_input}"
                    }, timeout=30)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("#### Security Audit Findings")
                        if sec_res.status_code == 200:
                            st.info(sec_res.json()["answer"])
                        else:
                            st.error("Failed to load security audit.")
                            
                    with c2:
                        st.markdown("#### Documentation Audit Findings")
                        if doc_res.status_code == 200:
                            st.info(doc_res.json()["answer"])
                        else:
                            st.error("Failed to load documentation audit.")
                            
                except Exception as e:
                    st.error(f"Error executing analysis audit: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== TAB 3: Side-by-Side Comparer ====================
with tab3:
    st.markdown("### Repository Comparative Matrix")
    st.caption("Provide multiple repository names separated by commas to compare their primary metrics side-by-side.")

    c_repos_input = st.text_input("Repositories to Compare", value="facebook/react, vuejs/core, angular/angular")
    compare_btn = st.button("Generate Comparison Table", use_container_width=True)

    if compare_btn:
        if not backend_running:
            st.error("Backend API is offline.")
        else:
            with st.spinner("Generating comparative matrix..."):
                try:
                    res = httpx.post(f"{API_URL}/compare", json={"repo_list_str": c_repos_input})
                    if res.status_code == 200:
                        report_table = res.json()["report"]
                        st.markdown(report_table)
                    else:
                        st.error("Failed to generate repository comparisons.")
                except Exception as e:
                    st.error(f"Error connecting to compare API: {e}")

# ==================== TAB 4: A2A Discovery ====================
with tab4:
    st.markdown("### Agent Capability Discovery (A2A Card)")
    st.caption("Expose agent capabilities, versioning, API endpoints, and matching skill tags to external AI systems.")

    if backend_running:
        try:
            res = httpx.get(f"{API_URL}/devpulse")
            if res.status_code == 200:
                card_data = res.json()
                st.subheader(f"Agent Card: {card_data['name']}")
                st.write(f"**Description**: {card_data['description']}")
                st.write(f"**Version**: {card_data['version']}")
                st.write(f"**A2A Endpoint**: `{card_data['endpoint']}`")
                
                st.markdown("#### Registered Agent Skills")
                for s in card_data["skills"]:
                    tags_html = " ".join([f"`{t}`" for t in s["tags"]])
                    st.markdown(f"- **{s['id']}**: {s['description']}\n  - Tags: {tags_html}")
                    
                st.markdown("#### Complete JSON Payload")
                st.json(card_data)
            else:
                st.error("Backend failed to return Agent Card.")
        except Exception as e:
            st.error(f"Error fetching Agent Card: {e}")
    else:
        st.warning("Backend offline. Cannot fetch agent capability card.")
