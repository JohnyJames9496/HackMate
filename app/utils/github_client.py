import httpx
from typing import Dict, Optional

GITHUB_API = "https://api.github.com"

def get_github_username_from_url(github_url: str) -> Optional[str]:
    if not github_url:
        return None
    parts = github_url.rstrip("/").split("/")
    return parts[-1] if parts else None


def fetch_github_data(github_url: str) -> Dict:
    username = get_github_username_from_url(github_url)
    if not username:
        return {}

    try:
        with httpx.Client(timeout=10) as client:
            user_response = client.get(
                f"{GITHUB_API}/users/{username}",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            if user_response.status_code != 200:
                return {}

            user_data = user_response.json()

            repos_response = client.get(
                f"{GITHUB_API}/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"},
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            repos_data = repos_response.json() if repos_response.status_code == 200 else []

            languages = {}
            for repo in repos_data:
                if repo.get("language"):
                    lang = repo["language"]
                    languages[lang] = languages.get(lang, 0) + 1

            return {
                "username": username,
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "languages": languages,
                "total_stars": sum(
                    r.get("stargazers_count", 0) for r in repos_data
                )
            }

    except Exception:
        return {}


def calculate_github_activity_score(github_data: Dict) -> float:
    if not github_data:
        return 0.0

    repo_count = github_data.get("public_repos", 0)
    followers = github_data.get("followers", 0)
    stars = github_data.get("total_stars", 0)

    repo_score = min(repo_count / 20, 1.0)
    follower_score = min(followers / 50, 1.0)
    star_score = min(stars / 30, 1.0)

    return round(
        (repo_score * 0.5) +
        (follower_score * 0.3) +
        (star_score * 0.2),
        4
    )