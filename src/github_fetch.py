"""
Fetch canonical READMEs for all public repositories of a user via the
GitHub REST API (never HTML scraping).

- GET /user/{user}/repos handles listing; GET /repos/{user}/{repo}/readme
  lets GitHub select the default README regardless of name/case/extension
  (README.md, README.rst, README.txt, plain README, ...).
- Content is stored raw and untouched next to a metadata JSON sidecar
  containing repo, source URL, timestamp, content hash and README type.
"""

from pathlib import Path
import base64
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import requests
from typing import Dict, List, Optional


GITHUB_USERNAME = "Manas-Dikshit"
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "github"
META_PATH = DATA_DIR / "readme_meta.json"
REPOS_PATH = DATA_DIR / "repos.json"

BASE_URL = "https://api.github.com"

MIN_README_CHARS = 20          # below this, treat the README as invalid
MAX_RETRIES = 3                # per request
RETRY_BACKOFF_SECONDS = 2      # exponential base
REQUEST_TIMEOUT = 15           # seconds


def _load_env() -> None:
    """
    Minimal .env loader: sets KEY=VALUE pairs into os.environ
    without overriding existing variables. No external dependency.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_env()

session = requests.Session()
_headers = {"Accept": "application/vnd.github+json"}

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if GITHUB_TOKEN:
    _headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

session.headers.update(_headers)


class GitHubError(RuntimeError):
    """Unrecoverable GitHub API failure after retries."""


def api_get(
    url: str,
    max_retries: int = MAX_RETRIES,
    timeout: float = REQUEST_TIMEOUT
) -> requests.Response:
    """
    GET with timeout, retries and rate-limit handling.

    Raises GitHubError with a clear message when all attempts fail.
    """

    last_error = ""

    for attempt in range(1, max_retries + 1):

        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            last_error = f"network error: {exc}"
            response = None

        if response is not None:

            # Rate limited: respect the reset time if sane, then fail hard.
            if response.status_code == 403 and \
                    response.headers.get("X-RateLimit-Remaining") == "0":

                reset = response.headers.get("X-RateLimit-Reset")
                wait = 5
                if reset and reset.isdigit():
                    wait = min(
                        max(int(reset) - int(time.time()) + 1, 5),
                        120
                    )
                raise GitHubError(
                    "GitHub rate limit exceeded. "
                    f"Resets in ~{wait}s. Set GITHUB_TOKEN to raise limits."
                )

            # Retryable server/network conditions.
            if response.status_code >= 500 or response.status_code == 429:
                last_error = f"HTTP {response.status_code}"
                response = None

        if response is not None:
            return response

        if attempt < max_retries:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise GitHubError(f"GET {url} failed after {max_retries} tries "
                      f"({last_error}).")


def get_repositories() -> List[Dict]:
    """
    Fetch all repositories for the user. Handles pagination.
    """

    repositories: List[Dict] = []
    page = 1

    while True:

        response = api_get(
            f"{BASE_URL}/users/{GITHUB_USERNAME}/repos"
            f"?per_page=100&page={page}"
        )

        if response.status_code == 404:
            raise GitHubError(
                f"GitHub user '{GITHUB_USERNAME}' not found."
            )

        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        repositories.extend(batch)
        page += 1

    return repositories


def _decode_readme(payload: Dict) -> Optional[str]:
    """
    Decode base64 README content from the API payload.
    Returns None when the content is unusable or was corrupted by
    GitHub's sanitization (replacement chars present).
    """

    encoded = payload.get("content")

    if payload.get("encoding") != "base64" or not encoded:
        return None

    raw = base64.b64decode(encoded)

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        # Non-UTF8 file (UTF-16, latin-1, ...): the JSON endpoint already
        # mangled it; caller must re-fetch raw bytes instead.
        return None

    if "\ufffd" in text:
        return None

    return text


def _fetch_raw_bytes(download_url: str) -> Optional[bytes]:
    """
    Fetch the exact file bytes from the raw download URL.
    """

    if not download_url:
        return None

    response = api_get(download_url)

    if response.status_code != 200:
        return None

    return response.content


def _decode_bytes(raw: bytes) -> str:
    """
    Decode file bytes to text, handling UTF-8, UTF-16 (BOM) and finally
    a lossy latin-1 fallback so nothing silently disappears.
    """

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass

    try:
        return raw.decode("utf-16")
    except UnicodeDecodeError:
        pass

    print("Warning: unknown encoding; falling back to lossy latin-1.")
    return raw.decode("latin-1")


def fetch_readme(repo_name: str) -> Optional[Dict]:
    """
    Fetch the canonical README for one repository.

    Returns None when the repository genuinely has no README (404).
    Raises GitHubError for unrecoverable API failures.

    Validates the response: decodable, non-trivially-short, and complete
    (decoded length must match the size reported by GitHub).
    """

    url = f"{BASE_URL}/repos/{GITHUB_USERNAME}/{repo_name}/readme"

    for attempt in range(1, MAX_RETRIES + 1):

        response = api_get(url)

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            # 401/403 etc: unlikely to improve by retrying the same way,
            # but surface a clear message.
            raise GitHubError(
                f"README fetch for '{repo_name}' failed: "
                f"HTTP {response.status_code}"
            )

        payload = response.json()
        content = _decode_readme(payload)

        reported_size = payload.get("size", -1)

        if content is None or (
            reported_size >= 0
            and len(content.encode("utf-8")) != reported_size
        ):
            # JSON endpoint unusable (non-UTF8 file) or response looks
            # truncated: fetch exact bytes from the raw download URL.
            raw = _fetch_raw_bytes(payload.get("download_url", ""))

            if raw is None:
                print(f"  Warning: could not fetch raw README for "
                      f"{repo_name}.")
                if content is None:
                    content = None  # keep None -> handled below
            else:
                if len(raw) < max(reported_size, 0):
                    print(f"  Truncated raw response ({len(raw)} < "
                          f"{reported_size} bytes); retrying "
                          f"({attempt}/{MAX_RETRIES})...")
                    continue

                content = _decode_bytes(raw)

        if content is None:
            print(f"  Warning: unreadable README payload for {repo_name}.")
        elif len(content.strip()) < MIN_README_CHARS:
            print(f"  Warning: README for {repo_name} suspiciously short "
                  f"({len(content)} chars); treating as missing.")
            return None
        else:
            return {
                "content": content,
                "path": payload.get("path", "README.md"),
                "name": payload.get("name", "README.md"),
                "html_url": payload.get("html_url", ""),
                "github_sha": payload.get("sha", ""),
                "size_bytes": reported_size,
                "readme_type": Path(payload.get("name", "README.md"))
                .suffix.lstrip(".").lower() or "plain",
            }

    raise GitHubError(
        f"README for '{repo_name}' kept arriving truncated "
        f"({MAX_RETRIES} attempts)."
    )


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_meta() -> Dict:
    if META_PATH.exists():
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    return {}


def store_readme(
    repo_name: str,
    fetched: Dict
) -> str:
    """
    Persist the raw README exactly as fetched plus its metadata.

    Returns the action taken: 'created', 'updated' or 'unchanged'.
    Stale local copies (hash differs from freshly fetched content) are
    replaced; identical content is left untouched.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    target = DATA_DIR / f"{repo_name}.md"
    meta = load_meta()
    previous = meta.get(repo_name, {})

    new_hash = _content_hash(fetched["content"])

    if target.exists() and previous.get("sha256") == new_hash:
        return "unchanged"

    action = "updated" if target.exists() else "created"

    # Write raw, byte-exact content. No headers, no cleaning.
    with open(target, "w", encoding="utf-8", newline="") as f:
        f.write(fetched["content"])

    meta[repo_name] = {
        "repo": repo_name,
        "path": fetched["path"],
        "readme_type": fetched["readme_type"],
        "source_url": fetched["html_url"],
        "github_sha": fetched["github_sha"],
        "size_bytes": fetched["size_bytes"],
        "sha256": new_hash,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    META_PATH.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Remove legacy duplicate copies once the canonical file exists.
    legacy = DATA_DIR / f"{repo_name}_README.md"
    if legacy.exists():
        legacy.unlink()

    return action


def _remove_stale_local(repo_name: str, meta: Dict) -> bool:
    """
    Delete local README copies for a repository that no longer has one
    (or only has an empty/invalid one). Returns True if files were removed.
    """

    removed = False

    for name in (f"{repo_name}.md", f"{repo_name}_README.md"):
        target = DATA_DIR / name
        if target.exists():
            target.unlink()
            removed = True

    if repo_name in meta:
        del meta[repo_name]

    return removed


def fetch_all_readmes() -> Dict:
    """
    Refresh every repository README. Returns a summary report.
    """

    repositories = get_repositories()
    print(f"Found {len(repositories)} repositories.\n")

    stats = {
        "repositories": len(repositories),
        "fetched": 0,
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "removed_stale": 0,
        "missing_readme": [],
        "failed": [],
    }

    for repo in repositories:

        repo_name = repo["name"]
        print(f"Fetching {repo_name}")

        try:
            fetched = fetch_readme(repo_name)
        except GitHubError as exc:
            print(f"  FAILED: {exc}")
            stats["failed"].append({"repo": repo_name, "error": str(exc)})
            continue

        if fetched is None:
            stats["missing_readme"].append(repo_name)
            meta = load_meta()
            if _remove_stale_local(repo_name, meta):
                stats["removed_stale"] += 1
                META_PATH.write_text(
                    json.dumps(meta, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                print(f"  Removed stale local copy (no README upstream).")
            continue

        stats["fetched"] += 1

        action = store_readme(repo_name, fetched)
        stats[action] += 1

    REPOS_PATH.write_text(
        json.dumps([r["name"] for r in repositories], indent=2),
        encoding="utf-8"
    )

    print(
        f"\nDone. fetched={stats['fetched']} "
        f"(created={stats['created']}, updated={stats['updated']}, "
        f"unchanged={stats['unchanged']}), "
        f"missing={len(stats['missing_readme'])}, "
        f"failed={len(stats['failed'])}"
    )

    return stats


if __name__ == "__main__":
    report = fetch_all_readmes()

    if report["missing_readme"]:
        print("\nRepositories without README:")
        for name in report["missing_readme"]:
            print(f"  - {name}")

    if report["failed"]:
        print("\nFailed repositories:")
        for item in report["failed"]:
            print(f"  - {item['repo']}: {item['error']}")
