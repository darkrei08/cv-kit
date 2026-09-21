"""Guard against publishing someone's personal data by accident.

A repository that generates CVs is one careless commit away from containing a real
person's address, phone number, tax code and family details. This script looks for
the shapes of that data, and for any exact term you supply locally.

WHAT IT SCANS
-------------
Text files are read directly. Containers are opened too, because that is where a CV
repository actually keeps the data:

* ``.docx``, ``.xlsx``, ``.pptx``, ``.odt`` — ZIP archives; their XML parts are
  extracted and scanned. A Word document full of personal data would otherwise be
  invisible to a text scan.
* ``.pdf`` — text is extracted with PyMuPDF when it is installed. It is not a
  dependency of this script, so when it is missing the file is reported as NOT
  SCANNED rather than silently skipped.

Nothing else is silently skipped: every file that could not be read, and every file
whose type is not scanned, is listed in the summary. A clean verdict that hides what
it did not look at is worse than no verdict.

EXACT TERMS ARE NEVER COMMITTED
-------------------------------
The list of strings you must not publish is itself sensitive, so it is supplied from
outside:

    # Windows
    set CVKIT_PII_TERMS=Rossi,Maria Grazia,Via Esempio 1
    # macOS / Linux
    export CVKIT_PII_TERMS="Rossi,Maria Grazia,Via Esempio 1"

    python scripts/check_no_pii.py .
    python scripts/check_no_pii.py . --terms-file ../case-repo/.pii-terms

Without a terms file the scan can only find pattern-shaped data (e-mail, phone, tax
code, IBAN). It cannot know a name. The summary says so, every time.

Exit codes: 0 clean, 1 findings, 2 usage error, 3 clean but something was not
scanned and --strict was requested.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from html import unescape
from pathlib import Path

#: Directories never descended into. Two groups: version-control and cache noise,
#: which can never hold the data we care about, and the generated output of this very
#: repository, which would otherwise flood the scan with hex colours and geometry
#: numbers from its own demonstration documents. What is skipped is printed in the
#: summary, so a skip can never be mistaken for a clean result.
NEVER_DESCEND = {".git", ".hg", ".svn", ".venv", "venv", "__pycache__",
                 "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                 ".tox", "site-packages", ".ipynb_checkpoints"}
GENERATED_DESCEND = {"out", "dist", "build", ".eggs"}

def _is_generated(name: str) -> bool:
    return name in GENERATED_DESCEND or name.endswith(".egg-info")

TEXT_SUFFIXES = {".py", ".md", ".txt", ".rst", ".json", ".jsonl", ".yml", ".yaml",
                 ".toml", ".cfg", ".ini", ".html", ".htm", ".css", ".js", ".ts",
                 ".mmd", ".ps1", ".sh", ".bat", ".cmd", ".xml", ".svg", ".csv",
                 ".sql", ".env", ".properties", ""}

#: Containers whose payload is extracted and scanned.
ZIP_SUFFIXES = {".docx", ".docm", ".xlsx", ".xlsm", ".pptx", ".odt", ".ods", ".odp",
                ".epub"}
PDF_SUFFIXES = {".pdf"}

#: Binary files that cannot carry readable personal data.
OPAQUE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".ttf",
                   ".otf", ".woff", ".woff2", ".zip", ".gz", ".tar", ".7z", ".rar",
                   ".exe", ".dll", ".so", ".dylib", ".pyc", ".pyo", ".mp3", ".mp4",
                   ".wav", ".mov", ".avi"}

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "italian-tax-code": re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}(?:[\s-]?[A-Z0-9]{4}){2,7}[\s-]?[A-Z0-9]{1,4}\b"),
    # A social-security position number is written several ways: "MATRICOLA 12345678",
    # "Matricola **12345678**" in Markdown, "Posizione INPS : 1234567890 00". Markdown
    # emphasis and the alternate label defeated the first version of this pattern.
    "social-security-number": re.compile(
        r"(?:MATRICOLA|POSIZIONE\s+INPS)[\s:*_`]*((?:\d[\s.\-]?){6,}\d)", re.IGNORECASE
    ),
}

#: A phone number is a *candidate* match here and is confirmed by
#: :func:`looks_like_phone`. A single broad regex cannot do this job: a pattern loose
#: enough to accept "+39 333 444 5566" also accepts every colour code, version number
#: and decimal in a file, and a check that cries wolf is worse than no check.
PHONE_CANDIDATE = re.compile(r"(?<![\w.])(?:\+?\d[\d\s.\-()]{6,20}\d)(?![\w.])")

_HEX_OR_NUMBER = re.compile(r"[0-9a-fA-F]{4,12}")
_VERSION_OR_DECIMAL = re.compile(r"\d{1,4}(?:[.\-/]\d{1,4}){1,3}")


def looks_like_phone(value: str) -> bool:
    """Decide whether a digit run is a phone number rather than a number.

    Rules that together remove the false positives that matter: a plausible digit
    count, a separator or a national prefix, and no resemblance to a colour code, a
    version string, a decimal or a timestamp.
    """
    digits = re.sub(r"\D", "", value)
    if not 9 <= len(digits) <= 13:
        return False
    if value in ALLOWED:
        return False
    separated = bool(re.search(r"[\s.\-()]", value))
    national = digits.startswith("3") or digits.startswith("0") or \
        value.startswith("+") or digits.startswith("39")
    if not (separated or national):
        return False
    # A colour code or a short hexadecimal token is not a phone number.
    if not separated and _HEX_OR_NUMBER.fullmatch(digits):
        return False
    # Version strings, decimals, dates and IP-like sequences are not phone numbers.
    stripped = value.strip()
    if _VERSION_OR_DECIMAL.fullmatch(stripped):
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", stripped):
        return False
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", stripped):
        return False
    # A decimal number with a fractional part and no space grouping.
    if not separated and re.fullmatch(r"\d+\.\d+", stripped):
        return False
    return True

#: Values that are obviously not real. The demonstration tax code is here on purpose:
#: it has the shape of a real one so the check has something to catch in tests, and it
#: must not have a realistic value.
ALLOWED = {
    "example.com", "example.org", "example.net", "test@example.com",
    "giulia.bianchi@example.com", "maria.rossi@example.com",
    "+39 000 000 0000", "000 000 0000", "XXXXXX00X00X000X", "0.0.0.0",
    # Common false positives from the phone pattern inside version strings and dates.
    "1.2.3", "3.11",
}

PHONE_LIKE_WHITELIST = re.compile(r"^\d{1,2}[.:/]\d{1,2}([.:/]\d{1,4})?$")


def normalise(text: str) -> str:
    """Collapse whitespace and strip Markdown emphasis.

    A name split across a line break, or written with a doubled space, or wrapped in
    ** ** inside a Markdown file, all defeat a literal per-line comparison. Comparing
    on a normalised copy as well means those variations are still caught.
    """
    text = unescape(text)
    text = re.sub(r"[*_`]+", "", text)
    return re.sub(r"\s+", " ", text)


def flexible(term: str) -> re.Pattern:
    """A pattern that matches a term across any run of whitespace or punctuation."""
    parts = [re.escape(p) for p in re.split(r"[\s._-]+", term.strip()) if p]
    if not parts:
        return re.compile(r"(?!x)x")  # matches nothing
    return re.compile(r"[\s._\-*`]*".join(parts), re.IGNORECASE)


def mask(value: str) -> str:
    """Show enough to locate the problem, not enough to republish the data."""
    value = value.strip()
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * min(10, len(value) - 4)}{value[-2:]}"


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------
def text_of(path: Path) -> tuple[str | None, str]:
    """Return ``(text, reason)``. Text is None when the file could not be read."""
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        try:
            return path.read_text(encoding="utf-8", errors="replace"), ""
        except OSError as exc:
            return None, f"attention: unreadable ({exc.strerror or exc})"
    if suffix in ZIP_SUFFIXES:
        return _text_of_zip(path)
    if suffix in PDF_SUFFIXES:
        return _text_of_pdf(path)
    if suffix in OPAQUE_SUFFIXES:
        return "", "binary: image or archive, cannot hold readable text"
    return None, "unknown: format not scanned"


def _text_of_zip(path: Path) -> tuple[str | None, str]:
    chunks: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith((".xml", ".rels", ".txt", ".csv")):
                    continue
                try:
                    chunks.append(archive.read(name).decode("utf-8", errors="replace"))
                except Exception:
                    continue
    except Exception as exc:
        return None, f"attention: unreadable container ({exc})"
    if not chunks:
        return None, "attention: container holds no readable part"
    return "\n".join(chunks), ""


def _text_of_pdf(path: Path) -> tuple[str | None, str]:
    try:
        import pymupdf  # type: ignore
    except Exception:
        return None, "attention: PDF not scanned, install pymupdf (pip install 'cvkit[qa]')"
    try:
        document = pymupdf.open(str(path))
        return "\n".join(page.get_text() for page in document), ""
    except Exception as exc:
        return None, f"attention: unreadable PDF ({exc})"


#: The scanner cannot scan itself: its own documentation contains example phone
#: numbers and identifiers, which are exactly what the patterns look for. That is not
#: a hole — the file is a detector, not data — but it must be stated rather than left
#: as a mystery finding.
SELF = Path(__file__).resolve()


def iter_files(root: Path, descend_generated: bool = False):
    """Candidate files under root, plus the directories that were skipped.

    ``descend_generated`` is for the suspicious case: a repository whose own build
    output is under a directory called build, out or dist. The skip is reported either
    way, so a false negative is never silent, but this flag removes the skip entirely.
    """
    skipped: list[str] = []
    for path in root.rglob("*"):
        try:
            relative_parts = path.relative_to(root).parts
        except ValueError:
            relative_parts = path.parts
        if path.is_dir():
            name = path.name
            if name in NEVER_DESCEND or (_is_generated(name) and not descend_generated):
                skipped.append(str(path.relative_to(root)) if path.is_relative_to(root)
                               else str(path))
            continue
        if not path.is_file():
            continue
        if path.resolve() == SELF:
            continue
        if any(part in NEVER_DESCEND or (_is_generated(part) and not descend_generated)
               for part in relative_parts[:-1]):
            continue
        yield path
    # rglob cannot prune, so the skipped list is reported instead of hidden; the
    # generator above returns before these are used.
    iter_files.skipped = skipped


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------
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


def scan(root: Path, terms: list[str], *, show_values: bool = False,
         quiet: bool = False, descend_generated: bool = False) -> tuple[int, list[str]]:
    problems: list[tuple[Path, str, str, str]] = []
    not_scanned: list[str] = []
    scanned = 0

    term_patterns = [(term, flexible(term)) for term in terms]
    iter_files.skipped = []
    for path in iter_files(root, descend_generated):
        raw, reason = text_of(path)
        if raw is None:
            not_scanned.append(f"{_relative(path, root)} — {reason}")
            continue
        if reason:
            not_scanned.append(f"{_relative(path, root)} — {reason}")
        if not raw:
            scanned += 1
            continue
        scanned += 1
        pretty = normalise(raw)

        for line_number, line in enumerate(raw.splitlines(), start=1):
            for name, pattern in PATTERNS.items():
                for match in pattern.finditer(line):
                    value = match.group(0)
                    if _ignorable(value):
                        continue
                    problems.append((path, name, value, f"line {line_number}"))
            for match in PHONE_CANDIDATE.finditer(line):
                value = match.group(0)
                if looks_like_phone(value) and not any(
                        a in value for a in ALLOWED):
                    problems.append((path, "phone", value, f"line {line_number}"))

        for term, pattern in term_patterns:
            if pattern.search(pretty):
                problems.append((path, "exact-term", term, "anywhere in file"))

    skipped_dirs = getattr(iter_files, "skipped", [])
    if not problems:
        if not quiet:
            print(f"no personal data found under {root}")
            print(f"  scanned: {scanned} file(s), {len(term_patterns)} exact term(s)")
            if not terms:
                print("  WARNING: no exact terms supplied, so the scan can only find "
                      "pattern-shaped data (e-mail, phone, tax code, IBAN).\n"
                      "           A name is invisible to it. Pass --terms-file or set "
                      "CVKIT_PII_TERMS.")
            if skipped_dirs:
                print(f"  directories not descended into: {len(skipped_dirs)}")
                for entry in sorted(set(skipped_dirs))[:10]:
                    print(f"    - {entry}/")
            if not_scanned:
                print(f"  NOT SCANNED: {len(not_scanned)} file(s):")
                for entry in not_scanned:
                    print(f"    - {entry}")
        return 0, not_scanned

    print(f"possible personal data found under {root}:")
    for path, name, value, where in problems:
        shown = value if show_values else mask(value)
        print(f"  {_relative(path, root)} [{name}] {where}: {shown}")
    print(f"\n  scanned: {scanned} file(s); {len(not_scanned)} not scanned")
    if not_scanned and len(not_scanned) <= 20:
        for entry in not_scanned:
            print(f"    - {entry}")
    print("\nIf this is intentional, for instance inside a private repository, review "
          "each line.\nIf the file belongs to a public repository, remove the data "
          "before committing.")
    return 1, not_scanned


def _ignorable(value: str) -> bool:
    return value in ALLOWED or any(a in value for a in ALLOWED) \
        or bool(PHONE_LIKE_WHITELIST.match(value))


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".",
                        help="directory to scan (default: the current one)")
    parser.add_argument("--terms-file", default=None,
                        help="file with one exact term per line; never commit it")
    parser.add_argument("--show-values", action="store_true",
                        help="print the matched values in full (they appear in logs)")
    parser.add_argument("--strict", action="store_true",
                        help="also fail when a file could not be scanned")
    parser.add_argument("--descend-generated", action="store_true",
                        help="also scan directories named out, build, dist or "
                             "*.egg-info (they are skipped by default and the skip is "
                             "reported)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"{root} does not exist", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"{root} is not a directory", file=sys.stderr)
        return 2

    code, not_scanned = scan(root, load_terms(args.terms_file),
                             show_values=args.show_values, quiet=args.quiet,
                             descend_generated=args.descend_generated)
    if code == 0 and args.strict:
        needs_attention = [entry for entry in not_scanned
                           if "attention:" in entry]
        if needs_attention:
            print(f"strict mode: {len(needs_attention)} file(s) could not be scanned")
            return 3
    return code


if __name__ == "__main__":
    raise SystemExit(main())
