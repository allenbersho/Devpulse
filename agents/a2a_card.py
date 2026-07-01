from pydantic import BaseModel
from typing import List

class Skill(BaseModel):
    id: str
    description: str
    tags: List[str]

class AgentCard(BaseModel):
    name: str
    description: str
    version: str
    endpoint: str
    skills: List[Skill]

# -- DevPulse's own self-description ---------------------------------------
DEVPULSE_CARD = AgentCard(
    name="DevPulse",
    description="Enterprise-Grade Agentic GitHub Intelligence assistant backed by a multi-agent hierarchy.",
    version="2.0.0",
    endpoint="http://localhost:8000/devpulse",  # API host
    skills=[
        Skill(
            id="repo_info",
            description="Retrieve metadata, details, and contributors for a GitHub repository.",
            tags=["github", "repository", "stars", "contributors", "search"],
        ),
        Skill(
            id="issue_triage",
            description="Fetch open issues and triage/prioritize them.",
            tags=["github", "issues", "triage", "bugs", "priority"],
        ),
        Skill(
            id="release_notes",
            description="Retrieve and analyze the latest release notes and versions.",
            tags=["github", "release", "version", "changelog", "analyzer"],
        ),
        Skill(
            id="analytics",
            description="Calculate repository health scores, contributor commit trends, and bus factors.",
            tags=["github", "analytics", "health score", "bus factor", "insights"],
        ),
        Skill(
            id="security",
            description="Analyze security policies, license compliance, and maintenance vulnerabilities.",
            tags=["github", "security", "audit", "compliance", "vulnerabilities"],
        ),
        Skill(
            id="documentation",
            description="Audit repository README files and suggest enhancements.",
            tags=["github", "documentation", "audit", "readme", "suggestions"],
        ),
    ],
)

class AgentRegistry:
    def __init__(self):
        self.agents: list[AgentCard] = []

    def register(self, card: AgentCard):
        self.agents.append(card)

    def discover(self, tag: str) -> list[str]:
        return [a.name for a in self.agents for s in a.skills if tag in s.tags]
