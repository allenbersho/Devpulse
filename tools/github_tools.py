import os
import httpx
from datetime import datetime

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

_HEADERS = {"User-Agent": "DevPulse-MCP-Server"}
if GITHUB_TOKEN:
    _HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def _get(path: str, params: dict | None = None) -> tuple[int, dict]:
    """Single shared HTTP GET against the GitHub REST API."""
    try:
        r = httpx.get(
            f"{GITHUB_API}{path}",
            headers=_HEADERS,
            params=params,
            timeout=10,
            follow_redirects=True,
        )
        return r.status_code, (r.json() if r.content else {})
    except httpx.RequestError as e:
        return -1, {"message": f"Network error: {e}"}

def _friendly_error(status: int, data: dict, context: str) -> str:
    """Return user-friendly error messages for GitHub API responses."""
    if status == 403 and "rate limit" in str(data.get("message", "")).lower():
        return (
            f"ERROR: GitHub API rate limit exceeded. {context} "
            f"Unauthenticated requests are capped at 60/hour -- set the GITHUB_TOKEN "
            f"environment variable to raise this to 5,000/hour."
        )
    if status == 404:
        return f"ERROR: {context} not found on GitHub (404)."
    if status == -1:
        return f"ERROR: could not reach GitHub. {data.get('message')}"
    return (
        f"ERROR: GitHub API returned status {status} for {context}: "
        f"{data.get('message', 'unknown error')}"
    )

def search_repositories(query: str) -> str:
    """Search public GitHub repositories by keyword, topic, or language."""
    status, data = _get(
        "/search/repositories",
        params={"q": query, "sort": "stars", "per_page": 5},
    )
    if status != 200:
        return _friendly_error(status, data, f"search for '{query}'")

    items = data.get("items", [])
    if not items:
        return f"No repositories found for query: {query}"

    lines = [f"Top results for '{query}':"]
    for repo in items:
        lines.append(
            f"- {repo['full_name']} *{repo['stargazers_count']} -- {repo['description']}"
        )
    return "\n".join(lines)

def get_repo_details(owner: str, repo: str) -> str:
    """Get live details for a GitHub repository: stars, forks, license, description."""
    status, data = _get(f"/repos/{owner}/{repo}")
    if status != 200:
        return _friendly_error(status, data, f"{owner}/{repo}")

    license_name = (data.get("license") or {}).get("name", "No license")
    return (
        f"{data['full_name']}: {data.get('description', 'No description')}\n"
        f"{data['stargazers_count']:,} stars | {data['forks_count']:,} forks | "
        f"Language: {data.get('language', 'N/A')} | License: {license_name}\n"
        f"Open issues: {data['open_issues_count']} | Default branch: {data['default_branch']}"
    )

def list_open_issues(owner: str, repo: str, limit: int = 5) -> str:
    """List currently open issues for a GitHub repository."""
    status, data = _get(
        f"/repos/{owner}/{repo}/issues",
        params={"state": "open", "per_page": limit},
    )
    if status != 200:
        return _friendly_error(status, data, f"{owner}/{repo} issues")
    if not data:
        return f"{owner}/{repo} currently has no open issues."

    # Filter out Pull Requests, which GitHub returns in /issues endpoint
    issues = [item for item in data if "pull_request" not in item]

    lines = [f"Open issues for {owner}/{repo} (showing {len(issues)}):"]
    for issue in issues[:limit]:
        labels = ", ".join(l["name"] for l in issue.get("labels", [])) or "no labels"
        lines.append(f"- #{issue['number']}: {issue['title']} [{labels}]")
    return "\n".join(lines)

def list_contributors(owner: str, repo: str, limit: int = 5) -> str:
    """List the top contributors to a GitHub repository by commit count."""
    status, data = _get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": limit},
    )
    if status != 200:
        return _friendly_error(status, data, f"{owner}/{repo} contributors")
    if not data:
        return f"No contributor data available for {owner}/{repo}."

    lines = [f"Top contributors to {owner}/{repo}:"]
    for c in data:
        lines.append(f"- {c['login']}: {c['contributions']} commits")
    return "\n".join(lines)

def get_latest_release(owner: str, repo: str) -> str:
    """Get the latest published release for a GitHub repository."""
    status, data = _get(f"/repos/{owner}/{repo}/releases/latest")
    if status != 200:
        return _friendly_error(status, data, f"{owner}/{repo} latest release")

    return (
        f"Latest release of {owner}/{repo}: {data['tag_name']} ({data.get('name', '')})\n"
        f"Published: {data['published_at']}\n"
        f"Notes: {(data.get('body') or 'No release notes.')[:300]}"
    )

def get_security_audit(owner: str, repo: str) -> str:
    """Perform a security and maintenance audit on a GitHub repository."""
    status, repo_data = _get(f"/repos/{owner}/{repo}")
    if status != 200:
        return _friendly_error(status, repo_data, f"Security Audit for {owner}/{repo}")

    # Check community profile
    status_profile, profile_data = _get(f"/repos/{owner}/{repo}/community/profile")
    has_readme = False
    has_license = False
    has_security_policy = False
    
    if status_profile == 200:
        files = profile_data.get("files", {})
        has_readme = bool(files.get("readme"))
        has_license = bool(files.get("license"))
        has_security_policy = bool(files.get("security_policy"))
    else:
        # Fallback check
        has_license = repo_data.get("license") is not None

    archived = repo_data.get("archived", False)
    disabled = repo_data.get("disabled", False)
    pushed_at_str = repo_data.get("pushed_at", "")
    
    warnings = []
    if archived:
        warnings.append("- WARNING: This repository is archived. It is read-only and no longer maintained.")
    if disabled:
        warnings.append("- WARNING: This repository is disabled.")
    if not has_license:
        warnings.append("- WARNING: No license file detected. Reuse of this code might have legal implications.")
    if not has_readme:
        warnings.append("- WARNING: No README file detected. Documentation is missing.")
    if not has_security_policy:
        warnings.append("- NOTE: No security policy (SECURITY.md) found. Harder to report vulnerabilities.")

    # Activity Check
    if pushed_at_str:
        try:
            pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ")
            days_inactive = (datetime.utcnow() - pushed_at).days
            if days_inactive > 180:
                warnings.append(f"- WARNING: Inactive project. The last push was {days_inactive} days ago ({pushed_at_str[:10]}).")
        except ValueError:
            pass

    status_vuln, vuln_data = _get(f"/repos/{owner}/{repo}/advisories")
    # Note: advisories endpoint requires token / permissions, if it fails, just note it.
    vuln_count_str = "Unavailable (requires repository admin permissions)"
    if status_vuln == 200:
        vuln_count = len(vuln_data)
        vuln_count_str = f"{vuln_count} active advisories found"
        if vuln_count > 0:
            warnings.append(f"- WARNING: {vuln_count} public security advisories reported for this repository.")

    lines = [
        f"=== Security & Maintenance Audit for {owner}/{repo} ===",
        f"Archived Status: {'Archived' if archived else 'Active'}",
        f"License: {repo_data.get('license', {}).get('spdx_id', 'None') if repo_data.get('license') else 'None'}",
        f"README: {'Exists' if has_readme else 'Missing'}",
        f"Security Policy: {'Exists' if has_security_policy else 'Missing'}",
        f"Pushed Date: {pushed_at_str}",
        f"Security Advisories: {vuln_count_str}",
        "\nFindings:"
    ]
    if warnings:
        lines.extend(warnings)
    else:
        lines.append("- No immediate security or maintenance warnings found. The repo is active and contains standard documentation files.")

    return "\n".join(lines)

def get_documentation_audit(owner: str, repo: str) -> str:
    """Retrieve and inspect the README structure and content for a repository."""
    # Attempt to fetch README content
    status, data = _get(f"/repos/{owner}/{repo}/readme")
    if status != 200:
        return f"README Audit failed: {owner}/{repo} does not have a README file, or it could not be retrieved."

    readme_name = data.get("name", "README.md")
    readme_size = data.get("size", 0)
    download_url = data.get("download_url")

    # Let's inspect the actual README markdown using a quick download
    readme_content = ""
    if download_url:
        try:
            r = httpx.get(download_url, timeout=10)
            if r.status_code == 200:
                readme_content = r.text
        except Exception:
            pass

    checks = {
        "Has Installation Guide": any(kw in readme_content.lower() for kw in ["install", "setup", "pip install", "npm install", "get started"]),
        "Has Usage Examples": any(kw in readme_content.lower() for kw in ["usage", "example", "quickstart", "how to use"]),
        "Has Contribution Guidelines": any(kw in readme_content.lower() for kw in ["contribute", "contributing", "pull request"]),
        "Has License Reference": any(kw in readme_content.lower() for kw in ["license", "mit", "apache", "gpl"]),
    }

    lines = [
        f"=== Documentation Audit for {owner}/{repo} ===",
        f"README file name: {readme_name}",
        f"Size: {readme_size:,} bytes",
        "\nContent Checkpoints:"
    ]
    
    suggestions = []
    for check, passed in checks.items():
        status_symbol = "✓" if passed else "✗"
        lines.append(f" {status_symbol} {check}")
        if not passed:
            suggestions.append(f"- Add a section for '{check.replace('Has ', '')}' to make it easier for new users.")

    if readme_size < 1000:
        suggestions.append("- The README is relatively short (< 1KB). Consider expanding it with more detail.")

    lines.append("\nSuggestions:")
    if suggestions:
        lines.extend(suggestions)
    else:
        lines.append("- Outstanding README structure! All standard sections (Installation, Usage, Contributing, License) appear to be present.")

    return "\n".join(lines)
