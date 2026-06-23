from pathlib import Path
from typing import Dict, List, Tuple
from pypdf import PdfReader


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
    Load markdown files recursively and attach metadata.
    """

    root = Path(folder)

    if not root.exists():
        return []

    documents = []

    for file in root.rglob("*.md"):

        try:

            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()

            if not content:
                continue

            documents.append(
                {
                    "source": "github",
                    "repo": file.stem,
                    "path": str(
                        file.relative_to(root)
                    ),
                    "filename": file.name,
                    "text": content
                }
            )

        except Exception as exc:

            print(
                f"Skipped {file}: {exc}"
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
    Load all knowledge sources.
    """

    resume_path = "data/resume/resume.pdf"
    github_folder = "data/github"

    resume_text = load_resume(
        resume_path
    )

    github_documents = load_markdown_files(
        github_folder
    )

    contribution_text = (
        load_contribution_history(
            github_folder
        )
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
        }
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