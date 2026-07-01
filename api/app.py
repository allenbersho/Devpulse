import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Add project root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_graph.graph import graph
from memory.sqlite_memory import get_messages, save_message, clear_history, get_repo_context
from agents.a2a_card import DEVPULSE_CARD
import tools.analytics_tools as an

app = FastAPI(
    title="DevPulse API",
    description="Backend service for the Enterprise-Grade Agentic GitHub Intelligence Platform",
    version="2.0.0"
)

# Enable CORS for frontend flexibility
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    category: str
    answer: str
    current_repo: str
    tool_calls: List[Dict[str, Any]]

class ClearRequest(BaseModel):
    session_id: str

class HealthRequest(BaseModel):
    owner: str
    repo: str

class CompareRequest(BaseModel):
    repo_list_str: str

@app.get("/")
def read_root():
    return {"status": "running", "name": "DevPulse API Server", "version": "2.0.0"}

@app.get("/devpulse")
def get_a2a_card():
    """Endpoint for Agent-to-Agent (A2A) discovery."""
    return DEVPULSE_CARD

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Processes user message using the LangGraph Multi-Agent flow with sqlite memory."""
    try:
        # 1. Fetch persistent history from SQLite
        history = get_messages(request.session_id)
        
        # 2. Get current repo context if any
        cached_repo = get_repo_context(request.session_id)
        current_repo = f"{cached_repo[0]}/{cached_repo[1]}" if cached_repo else ""

        # 3. Invoke LangGraph
        result = graph.invoke({
            "session_id": request.session_id,
            "query": request.query,
            "history": history,
            "category": "",
            "tool_calls_made": [],
            "answer": "",
            "current_repo": current_repo
        })

        # 4. Save new conversation entries back to SQLite
        # Save user query
        save_message(request.session_id, "user", request.query)
        # Save tool execution log if tools were run
        if result["tool_calls_made"]:
            # Flatten or format tool details
            for tc in result["tool_calls_made"]:
                save_message(request.session_id, "tool", f"Executed {tc['tool']} with results: {tc['result']}")
        # Save agent final response
        save_message(request.session_id, "assistant", result["answer"])

        return ChatResponse(
            category=result["category"],
            answer=result["answer"],
            current_repo=result["current_repo"],
            tool_calls=result["tool_calls_made"]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
def clear_endpoint(request: ClearRequest):
    """Clears history and context repository for a session ID."""
    clear_history(request.session_id)
    return {"status": "success", "message": f"History cleared for session: {request.session_id}"}

@app.post("/health")
def health_endpoint(request: HealthRequest):
    """Calculate and return repository health scorecard directly."""
    try:
        score_text = an.get_repository_health_score(request.owner, request.repo)
        return {"report": score_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
def compare_endpoint(request: CompareRequest):
    """Compare multiple repositories side by side."""
    try:
        compare_text = an.compare_repositories(request.repo_list_str)
        return {"report": compare_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
