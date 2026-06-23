from pathlib import Path
import base64
import requests
from typing import List, Dict, Optional


GITHUB_USERNAME = "Manas-Dikshit"
OUTPUT_DIR = Path("data/github")

# Optional token to increase rate limits
GITHUB_TOKEN = None

BASE_URL = "https://api.github.com"


session = requests.Session()

headers = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

session.headers.update(headers)


def get_repositories() -> List[Dict]:
    """
    Fetch all repositories for a user.
    Handles GitHub pagination.
    """

    repositories = []
    page = 1

    while True:

        url = (
            f"{BASE_URL}/users/{GITHUB_USERNAME}/repos"
            f"?per_page=100&page={page}"
        )

        response = session.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        repositories.extend(batch)

        page += 1

    return repositories


def get_readme(repo_name: str) -> Optional[str]:
    """
    Retrieve README content from a repository.
    """

    url = (
        f"{BASE_URL}/repos/"
        f"{GITHUB_USERNAME}/{repo_name}/readme"
    )

    try:

        response = session.get(
            url,
            timeout=15
        )

        if response.status_code != 200:
            return None

        payload = response.json()

        encoded_content = payload.get("content")

        if not encoded_content:
            return None

        decoded = base64.b64decode(
            encoded_content
        ).decode(
            "utf-8",
            errors="ignore"
        )

        return decoded.strip()

    except requests.RequestException:
        return None


def save_repository(repo: Dict, readme: Optional[str]) -> None:
    """
    Save repository metadata and README.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    repo_name = repo["name"]

    path = OUTPUT_DIR / f"{repo_name}.md"

    content = f"""
Repository: {repo_name}

Description:
{repo.get("description") or "No description"}

Language:
{repo.get("language") or "Unknown"}

Topics:
{", ".join(repo.get("topics", []))}

Stars:
{repo.get("stargazers_count", 0)}

Repository URL:
{repo.get("html_url")}

README:

{readme or "No README found"}
"""

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(content.strip())


def fetch_all_readmes() -> None:
    """
    Fetch metadata and README for every repository.
    """

    repositories = get_repositories()

    print(f"Found {len(repositories)} repositories.\n")

    for repo in repositories:

        repo_name = repo["name"]

        print(f"Fetching {repo_name}")

        readme = get_readme(repo_name)

        save_repository(
            repo,
            readme
        )

    print("\nFinished.")


if __name__ == "__main__":
    fetch_all_readmes()