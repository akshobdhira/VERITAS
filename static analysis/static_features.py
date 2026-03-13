#!/usr/bin/env python3
"""
VERITAS MVP - Static Feature Extractor (Windows PE + generic binaries)

What it does (static-only, no execution):
1) Takes a file path (.exe/.dll or any binary)
2) Reads file bytes
3) Computes:
   - file size
   - SHA256 hash
   - Shannon entropy
   - number of printable strings
4) If PE file:
   - counts imported DLLs and imported functions (APIs)
5) Outputs:
   - JSON to stdout
   - optionally appends a CSV row

Usage:
  python static_features.py path/to/sample.exe
  python static_features.py path/to/sample.exe --csv dataset/static_features.csv
  python static_features.py path/to/sample.exe --json-out features.json

Dependencies:
  pip install pefile numpy
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from math import log2
from typing import Dict, Optional, Tuple

try:
    import pefile  # type: ignore
except ImportError:
    pefile = None


PRINTABLE_STR_RE = re.compile(rb"[ -~]{4,}")  # ASCII printable strings length >= 4


@dataclass
class StaticFeatures:
    path: str
    filename: str
    file_size: int
    sha256: str
    entropy: float
    num_strings: int
    is_pe: bool
    num_imported_dlls: int
    num_imported_functions: int


def read_file_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def shannon_entropy(data: bytes) -> float:
    """
    Shannon entropy in bits per byte. Typical:
    - Text-ish binaries: ~3-6
    - Packed/Compressed: often ~7-8
    """
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    ent = 0.0
    for c in freq:
        if c:
            p = c / n
            ent -= p * log2(p)
    return float(ent)


def count_printable_strings(data: bytes) -> int:
    """
    Counts ASCII printable string sequences length >= 4.
    """
    return len(PRINTABLE_STR_RE.findall(data))


def pe_import_counts(file_path: str) -> Tuple[bool, int, int]:
    """
    Returns:
      (is_pe, num_imported_dlls, num_imported_functions)
    """
    if pefile is None:
        # pefile not installed; we can still do generic features
        return (False, 0, 0)

    try:
        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
        )
    except Exception:
        return (False, 0, 0)

    num_dlls = 0
    num_funcs = 0

    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        num_dlls = len(pe.DIRECTORY_ENTRY_IMPORT)
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            # entry.imports contains imported functions
            try:
                num_funcs += len(entry.imports)
            except Exception:
                pass

    try:
        pe.close()
    except Exception:
        pass

    return (True, int(num_dlls), int(num_funcs))


def extract_static_features(file_path: str) -> StaticFeatures:
    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    data = read_file_bytes(file_path)

    is_pe, dlls, funcs = pe_import_counts(file_path)

    feats = StaticFeatures(
        path=file_path,
        filename=os.path.basename(file_path),
        file_size=len(data),
        sha256=sha256_hex(data),
        entropy=round(shannon_entropy(data), 6),
        num_strings=count_printable_strings(data),
        is_pe=is_pe,
        num_imported_dlls=dlls,
        num_imported_functions=funcs,
    )
    return feats


def ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(os.path.abspath(file_path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def append_to_csv(csv_path: str, feats: StaticFeatures) -> None:
    ensure_parent_dir(csv_path)
    row = asdict(feats)

    # Keep a stable column order
    fieldnames = list(row.keys())

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def write_json_out(json_path: str, feats: StaticFeatures) -> None:
    ensure_parent_dir(json_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(feats), f, indent=2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Static feature extraction for VERITAS MVP.")
    p.add_argument("file", help="Path to the sample file (.exe/.dll/any binary)")
    p.add_argument("--csv", help="Append features as a row into this CSV file")
    p.add_argument("--json-out", help="Write features to this JSON file")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        feats = extract_static_features(args.file)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    # Print JSON to stdout always
    print(json.dumps(asdict(feats), indent=2))

    if args.csv:
        try:
            append_to_csv(args.csv, feats)
            print(f"\n[OK] Appended to CSV: {os.path.abspath(args.csv)}")
        except Exception as e:
            print(f"[ERROR] Failed to write CSV: {e}", file=sys.stderr)
            return 1

    if args.json_out:
        try:
            write_json_out(args.json_out, feats)
            print(f"[OK] Wrote JSON: {os.path.abspath(args.json_out)}")
        except Exception as e:
            print(f"[ERROR] Failed to write JSON: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
