from pypdf import PdfReader
from pathlib import Path


# -------------------------
# RESUME LOADER
# -------------------------
def load_resume(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()


# -------------------------
# GITHUB README LOADER (ROBUST)
# -------------------------
def load_github_readmes(folder):
    path = Path(folder)

    readmes = []

    # Find ALL markdown files anywhere in folder
    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() == ".md":
            try:
                content = file.read_text(encoding="utf-8", errors="ignore").strip()

                if len(content) > 0:
                    readmes.append({
                        "repo": file.parent.name,
                        "file": file.name,
                        "text": content
                    })

            except Exception as e:
                print(f"⚠️ Skipped {file}: {e}")

    # Contribution history
    contrib_file = path / "contribution-history.txt"
    contrib_text = ""

    if contrib_file.exists():
        contrib_text = contrib_file.read_text(encoding="utf-8", errors="ignore").strip()

    return readmes, contrib_text


# -------------------------
# MAIN PIPELINE INPUT
# -------------------------
def load_all_data():
    resume_path = "data/resume/resume.pdf"
    github_path = "data/github"

    resume_text = load_resume(resume_path)
    readmes, contrib_text = load_github_readmes(github_path)

    return {
        "resume": resume_text,
        "readmes": readmes,
        "contribution": contrib_text
    }