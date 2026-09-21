"""Automatic quality checks.

A CV fails in ways that are invisible on screen and obvious to a parser or a
printer: a PDF that is really an image, a table that hides a job title, a second
page that ends 3 mm outside the printable area, a photo that should not be in a
portal file. This module measures those things instead of trusting the layout.

Two halves:

* :func:`inspect_docx` looks at the source document (structure: tables, images,
  text length). It needs nothing but python-docx.
* :func:`inspect_pdf` looks at the produced file (page count, real text layer,
  where content ends). It needs PyMuPDF; without it the checks that need
  rendering are reported as skipped rather than silently passing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .model import CV, Finding

#: A4 in points, and the point where the printable area ends with 14 mm margins.
A4_WIDTH_PT = 595.28
A4_HEIGHT_PT = 841.89


@dataclass
class Report:
    """The result of checking one file."""

    path: str
    findings: list[Finding] = field(default_factory=list)
    pages: int | None = None
    words: int | None = None
    skipped: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not [f for f in self.findings if f.level == "error"]

    def add(self, level: str, code: str, message: str, where: str = "") -> None:
        self.findings.append(Finding(level, code, message, where))

    def text(self) -> str:
        lines = [f"{Path(self.path).name}"
                 + (f"  ({self.pages} pages, {self.words} words)" if self.pages else "")]
        for finding in self.findings:
            lines.append("  " + str(finding))
        for note in self.skipped:
            lines.append(f"  SKIP {note}")
        if not self.findings and not self.skipped:
            lines.append("  all checks passed")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Source document
# ---------------------------------------------------------------------------
def inspect_docx(path: str | Path, *, expect_tables: int | None = None,
                 expect_images: int | None = None,
                 variant: str = "ats") -> Report:
    from docx import Document

    path = Path(path)
    report = Report(path=str(path))
    document = Document(str(path))

    tables = len(document.tables)
    images = len(document.inline_shapes)
    words = sum(len(p.text.split()) for p in document.paragraphs)

    if expect_tables is not None and tables != expect_tables:
        report.add("error", "unexpected-tables",
                   f"{tables} tables, expected {expect_tables} "
                   f"(a parser ignores layout tables)")
    if expect_images is not None and images != expect_images:
        report.add("error", "unexpected-images",
                   f"{images} images, expected {expect_images}")
    if variant in {"ats", "ats_en", "portal"}:
        if tables:
            report.add("error", "table-in-portal-variant",
                       f"{tables} table(s) in a portal-facing document")
        if images:
            report.add("error", "image-in-portal-variant",
                       f"{images} image(s) in a portal-facing document")

    # Text boxes and floating frames are invisible to most parsers.
    xml = document.element.xml
    for tag, label in (("w:txbxContent", "text box"),
                       ("w:framePr", "floating frame")):
        if tag in xml:
            level = "error" if variant in {"ats", "ats_en", "portal"} else "warning"
            report.add(level, "hidden-text-container", f"document contains a {label}")

    report.words = words
    return report


# ---------------------------------------------------------------------------
# Produced PDF
# ---------------------------------------------------------------------------
def inspect_pdf(path: str | Path, *, expect_pages: int | None = None,
                max_pages: int | None = None,
                forbid_tokens: tuple[str, ...] = (),
                forbid_images: bool = False,
                margin_mm: float = 14.0) -> Report:
    """Check a produced PDF.

    ``expect_pages`` asserts an exact count; ``max_pages`` asserts an upper bound.
    The upper bound is the rule that matters for a portal CV: a short career
    legitimately fits on one page, a long one must not spill onto a third.
    """
    path = Path(path)
    report = Report(path=str(path))
    try:
        import pymupdf
    except Exception:
        report.skipped.append("pymupdf not installed: page count, text layer and "
                              "overflow checks were not performed")
        return report

    document = pymupdf.open(str(path))
    report.pages = document.page_count
    limit = A4_HEIGHT_PT - (margin_mm * 72 / 25.4)
    text = ""
    for index, page in enumerate(document):
        text += page.get_text()
        blocks = page.get_text("blocks")
        if blocks:
            bottom = max(b[3] for b in blocks)
            if bottom > limit:
                report.add("error", "content-outside-printable-area",
                           f"content reaches {bottom:.0f} pt on page {index + 1}; the "
                           f"printable area ends at {limit:.0f} pt",
                           f"page {index + 1}")
        if forbid_images and page.get_images(full=True):
            report.add("error", "image-in-portal-variant",
                       f"page {index + 1} contains an embedded image", f"page {index + 1}")

    # A PDF with almost no extractable text is a scan or an outlined export.
    characters = len(text.strip())
    if characters < 400:
        report.add("error", "no-text-layer",
                   f"only {characters} characters of extractable text: the file is an "
                   f"image or the text is vectorised, and no parser can read it")
    if not text.strip():
        report.skipped.append("text extraction returned nothing: check the file opens")

    if expect_pages is not None and report.pages != expect_pages:
        report.add("error", "page-count",
                   f"{report.pages} pages, expected {expect_pages}")
    if max_pages is not None and report.pages > max_pages:
        report.add("error", "too-many-pages",
                   f"{report.pages} pages, the limit for this variant is {max_pages}")

    for token in forbid_tokens:
        if token and token.lower() in text.lower():
            # Mask the value: the token is by definition personal data, and this message
            # ends up in a build log, a CI transcript or an issue report. The guard
            # must not republish what it is guarding against.
            shown = f"{token[:2]}{'*' * 6}" if len(token) > 2 else "***"
            report.add("error", "forbidden-token",
                       f"a forbidden value ({shown}) must not appear in this variant")
    report.words = len(text.split())
    return report


# ---------------------------------------------------------------------------
# Everything at once
# ---------------------------------------------------------------------------
#: A file whose name contains one of these markers is candidate-facing and gets the
#: strict rules: no image, no personal data, a page ceiling.
PORTAL_MARKERS = ("ATS", "PORTAL")


def is_portal_variant(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in PORTAL_MARKERS)


def qa_cv(cv: CV, files: dict[str, Path], *, expect_pages: dict[str, int] | None = None,
          max_pages: int | None = 2, portal_names=None,
          forbid_tokens: tuple[str, ...] | None = None) -> list[Report]:
    """Check a model and every file produced from it.

    The strict rules are applied to portal-facing files only. A designed CV, a cover
    letter or an appendix is *supposed* to carry the address and the personal block:
    flagging those would be a false alarm, and false alarms train people to ignore
    the checks.

    ``files`` maps a variant name to a path; only ``.pdf`` and ``.docx`` are
    inspected, anything else is listed as skipped on purpose.
    """
    reports: list[Report] = []
    expect_pages = expect_pages or {}
    if forbid_tokens is None:
        forbid_tokens = default_forbidden_tokens(cv)
    portal = set(portal_names) if portal_names is not None else None

    model_report = Report(path="(model)")
    if cv.contact.personal and (portal is None or portal):
        model_report.add(
            "info", "personal-data-present",
            "the model declares personal data; it is rendered only by the designed "
            "and appendix variants, never by a portal variant")
    reports.append(model_report)

    for name, path in files.items():
        path = Path(path)
        if not path.exists():
            report = Report(path=str(path))
            report.add("error", "missing-file", "expected output does not exist")
            reports.append(report)
            continue
        strict = is_portal_variant(name) if portal is None else name in portal
        if path.suffix.lower() == ".pdf":
            reports.append(inspect_pdf(
                path,
                expect_pages=expect_pages.get(name),
                max_pages=max_pages if strict else None,
                forbid_tokens=forbid_tokens if strict else (),
                forbid_images=strict,
            ))
        elif path.suffix.lower() == ".docx":
            reports.append(inspect_docx(
                path,
                expect_tables=0 if strict else None,
                expect_images=0 if strict else None,
                variant="ats" if strict else "designed",
            ))
    return reports


def default_forbidden_tokens(cv: CV) -> tuple[str, ...]:
    """Tokens that must never appear in a portal-facing file.

    Built from the model itself: whatever is in the personal block, plus the full
    postal address, is forbidden by definition. Values shorter than six characters
    are skipped: they would match ordinary words and produce false alarms.
    """
    tokens: list[str] = []
    for value in cv.contact.personal.values():
        value = value.strip()
        if len(value) >= 6:
            tokens.append(value)
    if cv.contact.address:
        tokens.append(cv.contact.address.strip())
    return tuple(tokens)
