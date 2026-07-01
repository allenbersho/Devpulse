import os
import sys
import re
from models.model_client import get_client_and_model
from agent_graph.state import DevPulseState
from memory.sqlite_memory import get_repo_context, set_repo_context

# Add project root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

client, MODEL, BACKEND = get_client_and_model()

VALID_CATEGORIES = {
    "repo_info",
    "issue_triage",
    "release_notes",
    "analytics",
    "security",
    "documentation"
}

def classify_intent(state: DevPulseState) -> DevPulseState:
    """
    Classify the query into one of the specialist agent categories
    and extract/track the active repository in focus.
    """
    query = state["query"]
    session_id = state.get("session_id", "default")
    
    # Simple regex to look for "owner/repo" patterns
    repo_match = re.search(r'(?:github\.com/)?([a-zA-Z0-9\-._]+)/([a-zA-Z0-9\-._]+)', query)
    
    owner, repo = None, None
    if repo_match:
        o, r = repo_match.group(1), repo_match.group(2)
        # Filter out false positives
        if o.lower() not in ["github", "http", "https", "git", "npm", "pip", "python"] and r.lower() not in ["install", "com", "org", "py"]:
            owner, repo = o, r
            state["current_repo"] = f"{owner}/{repo}"
            set_repo_context(session_id, owner, repo)
            print(f" [router] extracted repository context: {owner}/{repo}")

    # If no repo matched in query, retrieve from SQLite memory
    if "current_repo" not in state or not state["current_repo"]:
        cached = get_repo_context(session_id)
        if cached:
            owner, repo = cached
            state["current_repo"] = f"{owner}/{repo}"
            print(f" [router] retrieved cached repository context: {owner}/{repo}")
        else:
            state["current_repo"] = ""

    # 2. LLM Classify category
    prompt = (
        "Classify this GitHub-related query into exactly one category:\n"
        "repo_info, issue_triage, release_notes, analytics, security, documentation\n\n"
        "repo_info = general repo stats, search, details, contributors\n"
        "issue_triage = anything about open issues, listing or triaging them\n"
        "release_notes = anything about latest release/version or changelogs\n"
        "analytics = health score, contribution stats, bus factor, repository comparisons, charts\n"
        "security = licensing, security advisories, vulnerability checks, archived/active status audit\n"
        "documentation = checking README, markdown structure, suggestion audits\n\n"
        f"Query: {query}\n\nReply with ONLY one of the six words."
    )
    
    result = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    category = result.choices[0].message.content.strip().lower()
    
    # Clean up output if LLM returned extra words
    for val in VALID_CATEGORIES:
        if val in category:
            category = val
            break
            
    if category not in VALID_CATEGORIES:
        category = "repo_info"
        
    state["category"] = category
    print(f" [router] classified query '{query[:40]}...' -> {state['category']}")
    return state

def route(state: DevPulseState) -> str:
    return state["category"]
