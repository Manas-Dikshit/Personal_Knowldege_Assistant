import os
import base64
import requests


GITHUB_USERNAME = "Manas-Dikshit"
OUTPUT_FOLDER = "data/github"


def get_repos():
    url = f"https://api.github.com/users/Manas-Dikshit/repos"
    repos = requests.get(url).json()
    return repos


def get_readme(repo_name):
    url = f"https://api.github.com/repos/Manas-Dikshit/{repo_name}/readme"

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return None

    content = res.json()["content"]
    decoded = base64.b64decode(content).decode("utf-8")

    return decoded


def save_readme(repo_name, content):
    if not content:
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    file_path = os.path.join(OUTPUT_FOLDER, f"{repo_name}_README.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fetch_all_readmes():
    repos = get_repos()

    for repo in repos:
        name = repo["name"]
        print(f"Fetching README: {name}")

        readme = get_readme(name)
        save_readme(name, readme)


if __name__ == "__main__":
    fetch_all_readmes()