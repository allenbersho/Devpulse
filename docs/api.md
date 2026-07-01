# DevPulse API Documentation

The FastAPI gateway server exposes REST endpoints to allow conversational interfaces, dashboards, and external agents to query repository intelligence.

## Endpoints

### 1. Conversational Chat
Exposes the multi-agent reasoning flow.
* **URL**: `/chat`
* **Method**: `POST`
* **Payload**:
```json
{
  "session_id": "session-123",
  "query": "Tell me about facebook/react"
}
```
* **Response**:
```json
{
  "category": "repo_info",
  "answer": "Detailed repository analysis...",
  "current_repo": "facebook/react",
  "tool_calls": [
    {
      "tool": "get_repo_details",
      "result": "facebook/react details..."
    }
  ]
}
```

### 2. A2A Capability Card
Provides Agent-to-Agent discovery profiles.
* **URL**: `/devpulse`
* **Method**: `GET`
* **Response**:
```json
{
  "name": "DevPulse",
  "description": "Agentic GitHub intelligence assistant...",
  "version": "2.0.0",
  "endpoint": "http://localhost:8000/devpulse",
  "skills": [
    {
      "id": "repo_info",
      "description": "Retrieve metadata, details...",
      "tags": ["github", "repository"]
    }
  ]
}
```

### 3. Quick Repository Health Check
Calculates the health score directly without running the multi-agent chat.
* **URL**: `/health`
* **Method**: `POST`
* **Payload**:
```json
{
  "owner": "facebook",
  "repo": "react"
}
```

### 4. Side-by-Side Comparison
Compares multiple repositories directly.
* **URL**: `/compare`
* **Method**: `POST`
* **Payload**:
```json
{
  "repo_list_str": "facebook/react, vuejs/core"
}
```
