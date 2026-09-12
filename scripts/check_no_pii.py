# -*- coding: utf-8 -*-
"""Guard against publishing someone's personal data by accident.

A repository that generates CVs is one careless commit away from containing a real
person's address, phone number, tax code and family details. This script looks for
the shapes of that data, and for any exact term you supply locally.

Generic detectors run everywhere and are safe to keep in a public repository:
e-mail addresses, phone numbers, Italian tax codes, IBAN, social security numbers.

Exact terms are supplied from outside, never committed, because the list of the very
strings you must not publish is itself sensitive:

    # Windows
    set CVKIT_PII_TERMS=Rossi,Maria Grazia,Via Esempio 1,XXXXXX00X00X000X
    # macOS / Linux
    export CVKIT_PII_TERMS="Rossi,Maria Grazia,Via Esempio 1,XXXXXX00X00X000X"

    python scripts/check_no_pii.py .
    python scripts/check_no_pii.py . --terms-file ../case-repo/.pii-terms

Exit code 1 when something is found, so it can run as a pre-push hook:

    #!/bin/sh
    python scripts/check_no_pii.py .
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache",
             ".mypy_cache", ".ruff_cache", "out", "dist", "build", ".eggs"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg",
                 ".ini", ".html", ".css", ".mmd", ".ps1", ".sh", ".svg", ".xml"}

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.-]?)?(?:3\d{2}[\s.-]?\d{6,7}"
                        r"|0\d{1,3}[\s.-]?\d{5,8})(?![\w.])"),
    "italian-tax-code": re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b"),
    # Italian social security number.
    "inps-number": re.compile(r"\bMATRICOLA\s+\d{8,}\b", re.IGNORECASE),
}

#: Values that are obviously not real. The demonstration tax code is here on purpose:
#: it has the shape of a real one so that the check has something to catch in tests,
#: and it must not have a realistic value.
ALLOWED = {
    "example.com", "example.org", "test@example.com", "giulia.bianchi@example.com",
    "maria.rossi@example.com", "+39 000 000 0000", "000 000 0000",
    "XXXXXX00X00X000X",
}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def load_terms(terms_file: str | None) -> list[str]:
    terms: list[str] = []
    env = os.environ.get("CVKIT_PII_TERMS", "")
    if env:
        terms += [t.strip() for t in env.split(",") if t.strip()]
    if terms_file:
        text = Path(terms_file).read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                terms.append(line)
    return terms


def scan(root: Path, terms: list[str], quiet: bool = False) -> int:
    problems: list[tuple[Path, int, str, str]] = []
    for path in iter_files(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as exc:  # unreadable file is worth knowing about
            if not quiet:
                print(f"  unreadable: {path} ({exc})")
            continue
        for number, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                for match in pattern.finditer(line):
                    value = match.group(0)
                    if value in ALLOWED or any(a in value for a in ALLOWED):
                        continue
                    problems.append((path, number, name, value))
            for term in terms:
                if term and term.lower() in line.lower():
                    problems.append((path, number, "exact-term", term))

    if not problems:
        if not quiet:
            print(f"no personal data found under {root} "
                  f"({len(terms)} exact term(s) checked)")
        return 0

    print(f"possible personal data found under {root}:")
    for path, number, name, value in problems:
        relative = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"  {relative}:{number}  [{name}]  {value}")
    print("\nIf this is intentional (for instance inside a private repository), "
          "review each line.\nIf the file is in a public repository, remove the data "
          "and rewrite history.")
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--terms-file", default=None,
                        help="file with one exact term per line (never commit it)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"{root} does not exist", file=sys.stderr)
        return 2
    return scan(root, load_terms(args.terms_file), quiet=args.quiet)


if __name__ == "__main__":
    raise SystemExit(main())
