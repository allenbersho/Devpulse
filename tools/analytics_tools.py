import os
from datetime import datetime
from tools.github_tools import _get, _friendly_error

def get_repository_health_score(owner: str, repo: str) -> str:
    """Calculate a repository health score (0-100) based on popularity, activity, issues, and files."""
    # 1. Fetch Repository Details
    status, repo_data = _get(f"/repos/{owner}/{repo}")
    if status != 200:
        return _friendly_error(status, repo_data, f"Health Score for {owner}/{repo}")

    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    open_issues = repo_data.get("open_issues_count", 0)
    pushed_at_str = repo_data.get("pushed_at", "")
    has_license = repo_data.get("license") is not None
    
    # 2. Fetch community profile for README check
    status_profile, profile_data = _get(f"/repos/{owner}/{repo}/community/profile")
    has_readme = False
    if status_profile == 200:
        has_readme = bool(profile_data.get("files", {}).get("readme"))
    else:
        # Fallback check
        has_readme = bool(repo_data.get("description"))

    # 3. Fetch Contributors count
    status_contrib, contrib_data = _get(f"/repos/{owner}/{repo}/contributors", params={"per_page": 50})
    contrib_count = len(contrib_data) if status_contrib == 200 else 0

    # 4. Calculation
    score = 50  # Base score
    breakdown = []

    # Popularity (Stars & Forks)
    stars_points = min(20, stars // 200)  # +1 point per 200 stars, up to 20
    score += stars_points
    breakdown.append(f"- Stars bonus: +{stars_points} points ({stars:,} stars)")

    forks_points = min(15, forks // 50)   # +1 point per 50 forks, up to 15
    score += forks_points
    breakdown.append(f"- Forks bonus: +{forks_points} points ({forks:,} forks)")

    # Open Issues penalty
    if open_issues > 0:
        # Penalty depends on stars ratio (more popular projects have more issues naturally)
        ratio = open_issues / max(1, stars)
        if ratio > 0.1:
            penalty = 15
        elif ratio > 0.05:
            penalty = 10
        elif ratio > 0.02:
            penalty = 5
        else:
            penalty = 0
        score -= penalty
        if penalty > 0:
            breakdown.append(f"- Open issues penalty: -{penalty} points ({open_issues} open issues)")
    else:
        breakdown.append("- Open issues: No penalty (0 open issues)")

    # Activity (Last Push)
    if pushed_at_str:
        try:
            pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ")
            days_inactive = (datetime.utcnow() - pushed_at).days
            if days_inactive <= 7:
                score += 20
                breakdown.append("- Activity: +20 points (Last commit within 7 days)")
            elif days_inactive <= 30:
                score += 15
                breakdown.append("- Activity: +15 points (Last commit within 30 days)")
            elif days_inactive <= 90:
                score += 5
                breakdown.append("- Activity: +5 points (Last commit within 90 days)")
            elif days_inactive > 180:
                score -= 15
                breakdown.append("- Activity penalty: -15 points (Inactive for > 6 months)")
            else:
                breakdown.append("- Activity: 0 points (Last commit within 6 months)")
        except ValueError:
            breakdown.append("- Activity: Could not calculate (invalid pushed_at date)")
    else:
        score -= 15
        breakdown.append("- Activity penalty: -15 points (No commit history found)")

    # Community Files
    if has_readme:
        score += 5
        breakdown.append("- Files: +5 points (README found)")
    else:
        score -= 5
        breakdown.append("- Files penalty: -5 points (README missing)")

    if has_license:
        score += 5
        breakdown.append("- Files: +5 points (License found)")
    else:
        score -= 5
        breakdown.append("- Files penalty: -5 points (License missing)")

    # Contributors Count
    if contrib_count >= 30:
        score += 15
        breakdown.append(f"- Contributors: +15 points (Robust contributor base of {contrib_count}+)")
    elif contrib_count >= 10:
        score += 10
        breakdown.append(f"- Contributors: +10 points (Active contributor base of {contrib_count})")
    elif contrib_count >= 3:
        score += 5
        breakdown.append(f"- Contributors: +5 points (Small contributor base of {contrib_count})")
    else:
        score -= 10
        breakdown.append(f"- Contributors penalty: -10 points (Solitary project, {contrib_count} contributors)")

    # Bounding
    score = max(0, min(100, score))
    
    # Grade
    if score >= 90:
        grade = "A (Excellent)"
    elif score >= 80:
        grade = "B (Good)"
    elif score >= 70:
        grade = "C (Fair)"
    elif score >= 50:
        grade = "D (Needs Improvement)"
    else:
        grade = "F (Critical/Unmaintained)"

    lines = [
        f"=== Repository Health Report: {owner}/{repo} ===",
        f"Overall Health Score: {score}/100",
        f"Rating Grade: {grade}",
        "\nScoring Breakdown:",
        "\n".join(breakdown)
    ]
    return "\n".join(lines)


def get_contributor_insights(owner: str, repo: str) -> str:
    """Analyze contributor metrics and calculate the bus factor."""
    status, data = _get(f"/repos/{owner}/{repo}/contributors", params={"per_page": 30})
    if status != 200:
        return _friendly_error(status, data, f"Contributor Insights for {owner}/{repo}")
    if not data:
        return f"No contributor insights available for {owner}/{repo}."

    total_top_commits = sum(c["contributions"] for c in data)
    
    # Calculate Bus Factor (number of contributors that make up > 50% of the commits)
    running_commits = 0
    bus_factor = 0
    for idx, c in enumerate(data):
        running_commits += c["contributions"]
        if running_commits > (total_top_commits / 2):
            bus_factor = idx + 1
            break
            
    if bus_factor == 0 and data:
        bus_factor = len(data)

    lines = [
        f"=== Contributor Insights for {owner}/{repo} ===",
        f"Sample size: Top {len(data)} contributors",
        f"Total commits analyzed: {total_top_commits:,}",
        f"Bus Factor: {bus_factor} (number of contributors making up >50% of commits)",
        "\nTop Contributors Profile:"
    ]

    for idx, c in enumerate(data[:5]):
        pct = (c["contributions"] / total_top_commits) * 100 if total_top_commits > 0 else 0
        lines.append(f"{idx+1}. {c['login']}: {c['contributions']:,} commits ({pct:.1f}%)")

    # Risk assessment
    if bus_factor == 1:
        lines.append("\nRisk Alert: High Bus Factor! The project is heavily dependent on a single developer.")
    elif bus_factor <= 3:
        lines.append("\nRisk Alert: Moderate Bus Factor. The project relies on a very small core team.")
    else:
        lines.append("\nHealth Status: Low Risk. The project has a distributed contribution pattern.")

    return "\n".join(lines)


def get_issue_analytics(owner: str, repo: str) -> str:
    """Classify and analyze open issues by category."""
    status, data = _get(
        f"/repos/{owner}/{repo}/issues",
        params={"state": "open", "per_page": 50},
    )
    if status != 200:
        return _friendly_error(status, data, f"Issue Analytics for {owner}/{repo}")
    
    # Filter out pull requests
    issues = [item for item in data if "pull_request" not in item]
    if not issues:
        return f"No open issues found for {owner}/{repo} to analyze."

    categories = {
        "Bug": 0,
        "Feature Request": 0,
        "Documentation": 0,
        "Question/Support": 0,
        "Uncategorized": 0
    }

    for issue in issues:
        title = issue.get("title", "").lower()
        labels = [l["name"].lower() for l in issue.get("labels", [])]
        
        # Check labels first
        is_bug = any("bug" in l or "error" in l or "defect" in l for l in labels)
        is_feature = any("feature" in l or "enhancement" in l or "proposal" in l for l in labels)
        is_doc = any("doc" in l or "wiki" in l for l in labels)
        is_question = any("question" in l or "support" in l or "help" in l or "discussion" in l for l in labels)

        # Check title if labels don't match
        if not (is_bug or is_feature or is_doc or is_question):
            is_bug = any(kw in title for kw in ["bug", "error", "fail", "crash", "issue", "defect"])
            is_feature = any(kw in title for kw in ["feature", "request", "add", "enhance", "support", "allow"])
            is_doc = any(kw in title for kw in ["doc", "readme", "document", "typo"])
            is_question = any(kw in title for kw in ["question", "how to", "why", "help", "?", "tutorial"])

        if is_bug:
            categories["Bug"] += 1
        elif is_feature:
            categories["Feature Request"] += 1
        elif is_doc:
            categories["Documentation"] += 1
        elif is_question:
            categories["Question/Support"] += 1
        else:
            categories["Uncategorized"] += 1

    total_issues = len(issues)
    lines = [
        f"=== Issue Analytics for {owner}/{repo} ===",
        f"Issues analyzed: {total_issues} open issues",
        "\nCategory Distribution:"
    ]

    for cat, count in categories.items():
        pct = (count / total_issues) * 100 if total_issues > 0 else 0
        bar = "█" * int(pct // 5)
        lines.append(f"- {cat:18} : {count:3} ({pct:5.1f}%) {bar}")

    # Summary analysis
    if categories["Bug"] > (total_issues * 0.5):
        lines.append("\nOverview: Majority of the open issues are Bugs. Recommend stabilization.")
    elif categories["Feature Request"] > (total_issues * 0.5):
        lines.append("\nOverview: Majority of the open issues are Feature Requests. High user demand for expansion.")
    else:
        lines.append("\nOverview: Balanced distribution of open issues across categories.")

    return "\n".join(lines)


def compare_repositories(repo_list_str: str) -> str:
    """Compare multiple repositories side by side. Specify list separated by commas, e.g. 'facebook/react, vuejs/core'"""
    repos = [r.strip() for r in repo_list_str.split(",") if r.strip()]
    if not repos:
        return "No repositories provided for comparison."

    comparison_data = []
    for r_name in repos:
        if "/" not in r_name:
            # Try searching to find the full name
            status, search_res = _get("/search/repositories", params={"q": r_name, "per_page": 1})
            if status == 200 and search_res.get("items"):
                r_name = search_res["items"][0]["full_name"]
            else:
                continue
        
        owner, name = r_name.split("/", 1)
        status, details = _get(f"/repos/{owner}/{name}")
        if status == 200:
            comparison_data.append(details)

    if not comparison_data:
        return "Failed to fetch details for any of the specified repositories."

    # Build markdown table
    headers = ["Metric"] + [r["full_name"] for r in comparison_data]
    separator = ["---"] * len(headers)
    
    rows = [
        ["Language"] + [r.get("language") or "N/A" for r in comparison_data],
        ["Stars"] + [f"{r.get('stargazers_count', 0):,}" for r in comparison_data],
        ["Forks"] + [f"{r.get('forks_count', 0):,}" for r in comparison_data],
        ["Open Issues"] + [f"{r.get('open_issues_count', 0):,}" for r in comparison_data],
        ["License"] + [(r.get("license") or {}).get("spdx_id") or "None" for r in comparison_data],
        ["Created At"] + [r.get("created_at")[:10] for r in comparison_data],
        ["Last Push"] + [r.get("pushed_at")[:10] for r in comparison_data],
    ]

    lines = [
        "=== Side-by-Side Repository Comparison ===",
        "",
        " | ".join(headers),
        " | ".join(separator)
    ]
    for row in rows:
        lines.append(" | ".join(row))

    return "\n".join(lines)
