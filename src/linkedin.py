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

from src.config import CHUNK_MAX_CHARS


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
) -> Tuple[Optional[List[str]], List[List[str]], List[str], int]:
    """
    Parse one CSV file.

    Returns (header, records, skipped_reasons, preamble_lines).

    - Detects LinkedIn-style preamble notes before the real header by
      choosing, among the first rows, the one with the most columns.
    - Quoted fields and embedded newlines are handled by csv.reader.
    - Empty rows are skipped; ragged rows are kept as-is (padded).
    """

    text = _read_text(path)
    lines = text.splitlines()

    try:
        parsed = [row for row in csv.reader(lines)]
    except csv.Error as exc:
        return None, [], [f"unparseable CSV: {exc}"], 0

    # Drop fully-empty rows but remember them (not errors).
    non_empty = [(i, row) for i, row in enumerate(parsed)
                 if any(field.strip() for field in row)]

    if not non_empty:
        return None, [], [], len(parsed)

    # Header = highest column count among the first few rows.
    head_window = [
        (i, row) for i, row in non_empty
        if i <= non_empty[0][0] + 10
    ]
    header_idx, header = max(head_window, key=lambda item: len(item[1]))

    if len(header) < 2:
        # A single-column table (e.g., Skills.csv) still needs >=1 column;
        # treat the widest row as header only if it has real field names.
        pass

    preamble = header_idx

    header = [field.strip() for field in header]

    records = []
    skipped = []

    for idx, row in parsed[header_idx + 1:]:

        values = [field.strip() for field in row]

        if not any(values):
            continue

        # Pad ragged rows so record rendering never crashes.
        if len(values) < len(header):
            values += [""] * (len(header) - len(values))

        records.append(values)

    _ = idx  # last loop var; not used further

    return header, records, skipped, preamble


# ---------------------------------------------------------------------
# Record -> semantic text (schema-driven, no hardcoded columns)
# ---------------------------------------------------------------------

_URN_NOISE_PREFIXES = ("urn:li:",)


def render_record(
    category: str,
    header: List[str],
    values: List[str],
    row_number: int
) -> Optional[Tuple[str, str]]:
    """
    Render one CSV row as semantic text.

    Returns (dedupe_key, text) or None when the row carries no
    meaningful information (all fields empty or just URNs).
    """

    lines = []
    meaningful = False

    for field, value in zip(header, values):

        if not value:
            continue

        # Raw object URNs alone carry no human-readable information.
        if value.lower().startswith(_URN_NOISE_PREFIXES) and len(value) < 40:
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

def load_linkedin_records(folder) -> List[Dict]:
    """
    Parse every CSV under folder into deduplicated rendered records.

    Returns [{"text", "metadata", "dedupe_key"}]. One malformed file
    never stops the others.
    """

    documents: List[Dict] = []
    seen: set = set()
    stats = {"files": 0, "records": 0, "duplicates": 0, "skipped": []}

    for path in discover_csvs(folder):

        stats["files"] += 1
        category = categorize(path)

        try:
            header, records, skipped, preamble = parse_csv(path)
        except Exception as exc:
            stats["skipped"].append({"file": path.name, "reason": str(exc)})
            continue

        if header is None:
            stats["skipped"].append(
                {"file": path.name, "reason": "empty or unreadable"}
            )
            continue

        if skipped:
            stats["skipped"].extend(
                {"file": path.name, "reason": reason} for reason in skipped
            )

        rel_path = str(path)

        for offset, values in enumerate(records):

            row_number = preamble + offset + 2  # 1-based CSV row number

            rendered = render_record(category, header, values, row_number)

            if rendered is None:
                continue

            dedupe_key, text = rendered

            if dedupe_key in seen:
                stats["duplicates"] += 1
                continue

            seen.add(dedupe_key)

            documents.append(
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

    documents.sort(key=lambda d: (
        d["metadata"]["file"], d["metadata"]["row"]
    ))

    documents_linkedin_stats = {
        "files": stats["files"],
        "records": stats["records"],
        "duplicates": stats["duplicates"],
        "skipped": stats["skipped"],
    }
    documents.append({"__stats__": documents_linkedin_stats})

    return documents


# ---------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------

def chunk_linkedin(
    folder,
    max_chars: int = CHUNK_MAX_CHARS
) -> List[Dict]:
    """
    Load all LinkedIn CSVs and pack their records into chunks.

    Records from the same file/category stay together (semantic
    coherence); a chunk never mixes files. Chunks carry metadata with
    the source file, category, and covered CSV row range.
    """

    loaded = load_linkedin_records(folder)

    stats_entry = loaded[-1]
    stats = stats_entry.get("__stats__", {}) if "__stats__" in stats_entry else {}
    records = loaded[:-1] if "__stats__" in stats_entry else loaded

    chunks: List[Dict] = []
    current: List[Dict] = []
    current_len = 0

    def emit() -> None:
        if not current:
            return

        first, last = current[0]["metadata"], current[-1]["metadata"]
        total = len(chunks)

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
                    "chunk_index": total + 1,
                },
            }
        )
        current.clear()

    _ = current_len

    for doc in records:

        meta = doc["metadata"]

        if current and (
            current[-1]["metadata"]["file"] != meta["file"]
            or current_len + 2 + len(doc["text"]) > max_chars
        ):
            emit()

        current.append(doc)
        current_len = sum(len(d["text"]) for d in current) + 2 * (len(current) - 1)

    emit()

    # Fill chunk_index/total_chunks now that counts are known.
    by_file: Dict[str, int] = {}
    for chunk in chunks:
        key = chunk["metadata"]["file"]
        by_file[key] = by_file.get(key, 0) + 1
        chunk["metadata"]["chunk_index"] = by_file[key]

    for chunk in chunks:
        chunk["metadata"]["total_chunks"] = by_file[chunk["metadata"]["file"]]

    chunks.append(
        {
            "text": "",
            "metadata": {},
            "__stats__": stats,
        }
    )

    return chunks


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
