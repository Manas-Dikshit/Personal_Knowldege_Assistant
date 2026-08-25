"""
LinkedIn CSV export ingestion.

Discovers all .csv files under data/linkedin/ recursively, parses them
robustly (BOM/UTF-16 encodings, quoted fields, embedded newlines,
preamble notes like in Connections.csv, empty/malformed rows), converts
every record into compact semantic text for embeddings, and packs
records into lossless chunks per category.

No LinkedIn filename or column name is hardcoded: categories derive
from file names and text rendering is schema-driven.
"""

import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from src.config import CHUNK_MAX_CHARS
except ImportError:  # direct script execution: python src/linkedin.py
    from config import CHUNK_MAX_CHARS


# ---------------------------------------------------------------------
# Discovery and low-level CSV reading
# ---------------------------------------------------------------------

def discover_csvs(folder) -> List[Path]:
    """
    All .csv files under folder, recursively, sorted by name.
    """

    root = Path(folder)

    if not root.exists():
        return []

    return sorted(p for p in root.rglob("*.csv") if p.is_file())


def _read_text(path: Path) -> str:
    """
    Decode a CSV file handling UTF-8/UTF-16 and BOMs.
    Falls back to latin-1 so a weird encoding never crashes ingestion.
    """

    raw = path.read_bytes()

    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")

    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    print(f"Warning: {path.name} is not UTF-8; using lossy latin-1.")
    return raw.decode("latin-1")


def parse_csv(
    path: Path
) -> Tuple[Optional[List[str]], List[List[str]]]:
    """
    Parse one CSV file.

    Returns (header, records). header is None for empty/unparseable files.

    - Detects LinkedIn-style preamble notes before the real header by
      choosing, among the first rows, the one with the most columns.
    - Quoted fields and embedded newlines are handled by csv.reader.
    - Fully-empty rows are dropped; ragged rows are padded, never dropped.
    """

    text = _read_text(path)
    lines = text.splitlines()

    try:
        parsed = [row for row in csv.reader(lines)]
    except csv.Error as exc:
        raise ValueError(f"unparseable CSV: {exc}")

    non_empty = [(i, row) for i, row in enumerate(parsed)
                 if any(field.strip() for field in row)]

    if not non_empty:
        return None, []

    # Header = highest column count among the first few non-empty rows.
    head_window = [
        (i, row) for i, row in non_empty
        if i <= non_empty[0][0] + 10
    ]
    header_idx, header = max(head_window, key=lambda item: len(item[1]))

    if len(header) < 1 or not any(field.strip() for field in header):
        raise ValueError("no usable header row found")

    preamble = header_idx
    width = len(header)
    header = [field.strip() for field in header]

    records = []

    for offset, row in enumerate(parsed[header_idx + 1:]):

        values = [field.strip() for field in row]

        if not any(values):
            continue

        # Pad ragged rows so record rendering never crashes.
        if len(values) < width:
            values += [""] * (width - len(values))

        # Keep the original 1-based CSV row number for provenance.
        records.append((preamble + offset + 2, values))

    return header, records


# ---------------------------------------------------------------------
# Record -> semantic text (schema-driven, no hardcoded columns)
# ---------------------------------------------------------------------

def render_record(
    category: str,
    header: List[str],
    values: List[str],
    row_number: int
) -> Optional[Tuple[str, str]]:
    """
    Render one CSV row as semantic text.

    Returns (dedupe_key, text) or None when the row carries no
    meaningful information (all fields empty or just object URNs).
    """

    lines = []
    meaningful = False

    for field, value in zip(header, values):

        if not value:
            continue

        # Raw object URNs alone carry no human-readable information.
        if value.lower().startswith("urn:li:") and len(value) < 40:
            continue

        meaningful = True

        label = field.replace("_", " ").strip()
        lines.append(f"{label}: {value}")

    if not meaningful:
        return None

    text = (
        f"LinkedIn {category} record (source row {row_number}):\n"
        + "\n".join(lines)
    )

    dedupe_key = hashlib.sha256(
        "\n".join(lines).encode("utf-8")
    ).hexdigest()

    return dedupe_key, text


def categorize(path: Path) -> str:
    """
    Category from the file name stem, generic for any LinkedIn export
    ("Positions" -> "positions", "Company Follows" -> "company follows").
    """

    return path.stem.replace("_", " ").strip().lower()


# ---------------------------------------------------------------------
# File-level loading
# ---------------------------------------------------------------------

def load_linkedin_records(folder) -> Tuple[List[Dict], Dict]:
    """
    Parse every CSV under folder into deduplicated rendered records.

    Returns (records, stats). Each record is
    {"text", "metadata", "dedupe_key"}. One malformed file never stops
    the others.
    """

    records: List[Dict] = []
    seen = set()
    stats = {"files": 0, "records": 0, "duplicates": 0, "skipped": []}

    for path in discover_csvs(folder):

        stats["files"] += 1
        category = categorize(path)

        try:
            header, rows = parse_csv(path)
        except Exception as exc:
            stats["skipped"].append({"file": path.name, "reason": str(exc)})
            continue

        if header is None:
            stats["skipped"].append(
                {"file": path.name, "reason": "empty file"}
            )
            continue

        if not rows:
            stats["skipped"].append(
                {"file": path.name, "reason": "no data rows"}
            )
            continue

        rel_path = str(path)

        for row_number, values in rows:

            rendered = render_record(category, header, values, row_number)

            if rendered is None:
                continue

            dedupe_key, text = rendered

            if dedupe_key in seen:
                stats["duplicates"] += 1
                continue

            seen.add(dedupe_key)

            records.append(
                {
                    "text": text,
                    "metadata": {
                        "source": "linkedin",
                        "file": path.name,
                        "path": rel_path,
                        "category": category,
                        "row": row_number,
                    },
                    "dedupe_key": dedupe_key,
                }
            )
            stats["records"] += 1

    records.sort(key=lambda d: (
        d["metadata"]["file"], d["metadata"]["row"]
    ))

    return records, stats


# ---------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------

def chunk_linkedin(
    folder,
    max_chars: int = CHUNK_MAX_CHARS
) -> Tuple[List[Dict], Dict]:
    """
    Load all LinkedIn CSVs and pack their records into chunks.

    Records from the same file stay together (semantic coherence); a
    chunk never mixes files. Chunk metadata carries source file,
    category, covered CSV row range, and chunk indexes per file.

    Returns (chunks, stats).
    """

    records, stats = load_linkedin_records(folder)

    chunks: List[Dict] = []
    current: List[Dict] = []
    current_len = 0

    def emit() -> None:
        nonlocal current_len

        if not current:
            return

        first, last = current[0]["metadata"], current[-1]["metadata"]

        chunks.append(
            {
                "text": "\n\n".join(d["text"] for d in current),
                "metadata": {
                    "source": "linkedin",
                    "file": first["file"],
                    "path": first["path"],
                    "category": first["category"],
                    "record_count": len(current),
                    "row_start": first["row"],
                    "row_end": last["row"],
                    "chunk_index": len(chunks),
                },
            }
        )
        current.clear()
        current_len = 0

    for doc in records:

        meta = doc["metadata"]

        if current and (
            current[-1]["metadata"]["file"] != meta["file"]
            or current_len + 2 + len(doc["text"]) > max_chars
        ):
            emit()

        current.append(doc)
        current_len += len(doc["text"]) + (2 if current_len else 0)

    emit()

    # Per-file totals for complete provenance metadata.
    totals: Dict[str, int] = {}
    for chunk in chunks:
        key = chunk["metadata"]["file"]
        totals[key] = totals.get(key, 0) + 1
        chunk["metadata"]["total_chunks"] = totals[key]

    for chunk in chunks:
        key = chunk["metadata"]["file"]
        chunk["metadata"]["total_chunks"] = totals[key]

    return chunks, stats


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from src.linkedin import chunk_linkedin

    folder = Path(__file__).resolve().parent.parent / "data" / "linkedin"
    chunks, stats = chunk_linkedin(folder)

    print(f"files       : {stats['files']}")
    print(f"records     : {stats['records']}")
    print(f"duplicates  : {stats['duplicates']}")
    print(f"skipped     : {len(stats['skipped'])}")
    for item in stats["skipped"]:
        print(f"  - {item['file']}: {item['reason']}")
    print(f"chunks      : {len(chunks)}")
