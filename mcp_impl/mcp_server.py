import os
import sys
from mcp.server.fastmcp import FastMCP

# Add the parent directory of this file to sys.path so we can import tools and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import tools
import tools.github_tools as gh
import tools.analytics_tools as an

mcp = FastMCP("DevPulse GitHub Intelligence Server")

# -- REGISTER TOOLS ---------------------------------------------------------
@mcp.tool()
def search_repositories(query: str) -> str:
    """Search public GitHub repositories by keyword, topic, or language."""
    return gh.search_repositories(query)

@mcp.tool()
def get_repo_details(owner: str, repo: str) -> str:
    """Get live details for a GitHub repository: stars, forks, license, description."""
    return gh.get_repo_details(owner, repo)

@mcp.tool()
def list_open_issues(owner: str, repo: str, limit: int = 5) -> str:
    """List currently open issues for a GitHub repository."""
    return gh.list_open_issues(owner, repo, limit)

@mcp.tool()
def list_contributors(owner: str, repo: str, limit: int = 5) -> str:
    """List the top contributors to a GitHub repository by commit count."""
    return gh.list_contributors(owner, repo, limit)

@mcp.tool()
def get_latest_release(owner: str, repo: str) -> str:
    """Get the latest published release for a GitHub repository."""
    return gh.get_latest_release(owner, repo)

@mcp.tool()
def get_security_audit(owner: str, repo: str) -> str:
    """Perform a security and maintenance audit on a GitHub repository."""
    return gh.get_security_audit(owner, repo)

@mcp.tool()
def get_documentation_audit(owner: str, repo: str) -> str:
    """Retrieve and inspect the README structure and content for a repository."""
    return gh.get_documentation_audit(owner, repo)

@mcp.tool()
def get_repository_health_score(owner: str, repo: str) -> str:
    """Calculate a repository health score (0-100) based on popularity, activity, issues, and files."""
    return an.get_repository_health_score(owner, repo)

@mcp.tool()
def get_contributor_insights(owner: str, repo: str) -> str:
    """Analyze contributor metrics and calculate the bus factor."""
    return an.get_contributor_insights(owner, repo)

@mcp.tool()
def get_issue_analytics(owner: str, repo: str) -> str:
    """Classify and analyze open issues by category."""
    return an.get_issue_analytics(owner, repo)

@mcp.tool()
def compare_repositories(repo_list_str: str) -> str:
    """Compare multiple repositories side by side. Specify list separated by commas, e.g. 'facebook/react, vuejs/core'"""
    return an.compare_repositories(repo_list_str)

# -- RESOURCE (read-only data, addressed by URI) ---------------------------
@mcp.resource("github://repo/{owner}/{repo}/summary")
def repo_summary_resource(owner: str, repo: str) -> str:
    """A pre-formatted, read-only snapshot of a repository's key stats."""
    status, data = gh._get(f"/repos/{owner}/{repo}")
    if status != 200:
        return gh._friendly_error(status, data, f"{owner}/{repo}")

    return (
        f"REPO SUMMARY: {data['full_name']}\n"
        f"Stars: {data['stargazers_count']} | Forks: {data['forks_count']} | "
        f"Open Issues: {data['open_issues_count']}\n"
        f"Created: {data['created_at']} | Last push: {data['pushed_at']}"
    )

# -- PROMPT (reusable instruction template) --------------------------------
@mcp.prompt()
def issue_triage_prompt() -> str:
    """A structured workflow for triaging a GitHub issue."""
    return """
    Review this GitHub issue and:
    1. Classify it as exactly one of: Bug / Feature Request / Question / Documentation
    2. Assign a priority: Critical / High / Medium / Low, based on impact described
    3. Suggest which existing label(s) it should carry
    4. Write a one-sentence summary suitable for a triage dashboard
    Be concise -- output should fit in 4 short lines.
    """

if __name__ == "__main__":
    import sys
    print("Starting DevPulse MCP Server from mcp_impl/mcp_server.py...", file=sys.stderr)
    mcp.run()
