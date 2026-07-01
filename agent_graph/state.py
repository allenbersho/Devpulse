from typing import TypedDict, List, Dict, Any

class DevPulseState(TypedDict):
    session_id: str
    query: str
    history: List[Dict[str, Any]]
    category: str
    tool_calls_made: List[Dict[str, Any]]
    answer: str
    current_repo: str  # Format: "owner/repo"
