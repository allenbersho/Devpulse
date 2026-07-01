import os
import sys
import asyncio
from langgraph.graph import StateGraph
from agent_graph.state import DevPulseState
from agent_graph.router import classify_intent, route

# Add parent directory of this file to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import agents
import agents.repo_agent as repo_agent
import agents.issue_agent as issue_agent
import agents.release_agent as release_agent
import agents.analytics_agent as analytics_agent
import agents.security_agent as security_agent
import agents.documentation_agent as documentation_agent

def repo_info_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(repo_agent.run(state))

def issue_triage_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(issue_agent.run(state))

def release_notes_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(release_agent.run(state))

def analytics_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(analytics_agent.run(state))

def security_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(security_agent.run(state))

def documentation_node(state: DevPulseState) -> DevPulseState:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(documentation_agent.run(state))

builder = StateGraph(DevPulseState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("repo_info", repo_info_node)
builder.add_node("issue_triage", issue_triage_node)
builder.add_node("release_notes", release_notes_node)
builder.add_node("analytics", analytics_node)
builder.add_node("security", security_node)
builder.add_node("documentation", documentation_node)

builder.add_conditional_edges(
    "classify_intent",
    route,
    {
        "repo_info": "repo_info",
        "issue_triage": "issue_triage",
        "release_notes": "release_notes",
        "analytics": "analytics",
        "security": "security",
        "documentation": "documentation",
    },
)

builder.set_entry_point("classify_intent")
builder.set_finish_point("repo_info")
builder.set_finish_point("issue_triage")
builder.set_finish_point("release_notes")
builder.set_finish_point("analytics")
builder.set_finish_point("security")
builder.set_finish_point("documentation")

graph = builder.compile()
