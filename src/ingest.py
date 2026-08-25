from pathlib import Path
import json
from typing import Dict, List

from pypdf import PdfReader

from src.config import GITHUB_DIR, LINKEDIN_DIR, RESUME_PATH
from src.linkedin import chunk_linkedin as load_linkedin_data


# ---------------------------------------------------------------------
# PDF Loader
# ---------------------------------------------------------------------

def load_resume(path: str) -> str:
    """
    Extract text from a PDF resume.
    """

    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Resume not found: {pdf_path}"
        )

    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)


# ---------------------------------------------------------------------
# Markdown Loader
# ---------------------------------------------------------------------

def load_markdown_files(folder: str) -> List[Dict]:
    """
    Load raw README files and attach fetch metadata.

    Each {repo}.md holds the complete raw README exactly as fetched from
    the GitHub API; readme_meta.json (written by github_fetch.py) carries
    source URL, fetched timestamp, content hash and README type.

    Legacy Repo_README.md duplicates are skipped only when their content
    is verifiably contained in the corresponding {repo}.md file.
    """

    root = Path(folder)

    if not root.exists():
        return []

    meta_path = root / "readme_meta.json"
    fetch_meta = {}
    if meta_path.exists():
        fetch_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    def _key(text: str) -> str:
        return "".join(text.split())

    files = sorted(root.rglob("*.md"))

    contents = {}
    for file in files:
        try:
            contents[file] = file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()
        except Exception as exc:
            print(f"Skipped {file}: {exc}")

    documents = []

    for file in files:

        if file.name == "readme_meta.json":
            continue

        content = contents.get(file, "")

        if not content:
            continue

        # Skip raw README duplicates that are already contained in Repo.md.
        if file.stem.endswith("_README"):
            base = file.with_name(
                f"{file.stem.removesuffix('_README')}.md"
            )
            if (
                base in contents
                and _key(contents.get(base, "")).find(_key(content)) != -1
            ):
                continue

        repo_name = file.stem.removesuffix("_README")
        extra = fetch_meta.get(repo_name, {})

        documents.append(
            {
                "source": "github",
                "repo": repo_name,
                "path": str(file.relative_to(root)),
                "filename": file.name,
                "text": content,
                # Fetch provenance (empty when metadata sidecar is absent).
                "source_url": extra.get("source_url", ""),
                "fetched_at": extra.get("fetched_at", ""),
                "content_hash": extra.get("sha256", ""),
                "readme_type": extra.get("readme_type", ""),
            }
        )

    return documents


# ---------------------------------------------------------------------
# Contribution History Loader
# ---------------------------------------------------------------------

def load_contribution_history(
    folder: str
) -> str:
    """
    Load contribution history if available.
    """

    path = (
        Path(folder)
        / "contribution-history.txt"
    )

    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    ).strip()


# ---------------------------------------------------------------------
# Generic Text Loader
# ---------------------------------------------------------------------

def load_text_files(
    folder: str,
    suffix: str = ".txt"
) -> List[Dict]:
    """
    Load arbitrary text files.
    """

    root = Path(folder)

    if not root.exists():
        return []

    documents = []

    for file in root.rglob(f"*{suffix}"):

        try:

            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()

            if text:

                documents.append(
                    {
                        "source": "text",
                        "path": str(
                            file.relative_to(root)
                        ),
                        "text": text
                    }
                )

        except Exception:

            continue

    return documents


# ---------------------------------------------------------------------
# Main Data Loader
# ---------------------------------------------------------------------

def load_all_data() -> Dict:
    """
    Load all knowledge sources. Missing optional sources are skipped
    with a warning instead of crashing the pipeline.
    """

    try:
        resume_text = load_resume(RESUME_PATH)
    except FileNotFoundError as exc:
        print(f"Warning: {exc}. Continuing without resume.")
        resume_text = ""

    github_documents = load_markdown_files(
        GITHUB_DIR
    )

    contribution_text = (
        load_contribution_history(
            GITHUB_DIR
        )
    )

    linkedin_chunks, linkedin_stats = load_linkedin_data(
        LINKEDIN_DIR
    )

    if linkedin_stats["files"]:
        print(
            f"LinkedIn: {linkedin_stats['records']} records from "
            f"{linkedin_stats['files']} files "
            f"({linkedin_stats['duplicates']} duplicates skipped, "
            f"{len(linkedin_stats['skipped'])} files/rows skipped)."
        )

    if (not resume_text and not github_documents
            and not contribution_text and not linkedin_chunks):
        raise RuntimeError(
            "No knowledge sources found in data/. Run "
            "'python src/github_fetch.py' or add a resume first."
        )

    return {
        "resume": {
            "source": "resume",
            "text": resume_text
        },

        "github": github_documents,

        "contributions": {
            "source": "contributions",
            "text": contribution_text
        },

        # Already chunked by the dedicated LinkedIn module.
        "linkedin_chunks": linkedin_chunks,
    }


# ---------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------

if __name__ == "__main__":

    data = load_all_data()

    print(
        "\nResume length:",
        len(data["resume"]["text"])
    )

    print(
        "Repositories loaded:",
        len(data["github"])
    )

    print(
        "Contribution characters:",
        len(data["contributions"]["text"])
    )