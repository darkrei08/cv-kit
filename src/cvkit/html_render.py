# -*- coding: utf-8 -*-
"""HTML/CSS route to PDF.

Why a second renderer exists at all: the Word route gives the best fidelity, but it
needs Word (Windows, or macOS with Office). The HTML route needs no office suite,
runs identically on Linux, macOS and Windows, and is the only route that can produce
a web page as a bonus. The trade-off is pagination, which a browser engine decides,
so the same quality checks are run on the result.

WeasyPrint is the engine used here: pure Python, no headless browser to install. If
it is absent, :func:`render_html` still works (you get the HTML) and only the PDF
step fails with an install hint.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from .model import CV

TEMPLATES = Path(__file__).parent / "templates"


def _style(name: str) -> str:
    path = TEMPLATES / name
    if not path.exists():
        raise FileNotFoundError(f"stylesheet missing: {path}")
    return path.read_text(encoding="utf-8")


def _ul(items, lead=None) -> str:
    if not items:
        return ""
    lines = []
    for item in items:
        if lead:
            key, value = item
            lines.append(f"<li><span class=\"lead\">{escape(key)}</span> – {escape(value)}</li>")
        else:
            lines.append(f"<li>{escape(item)}</li>")
    return "<ul>" + "".join(lines) + "</ul>"


def _profile_block(cv: CV) -> str:
    if not cv.profile:
        return ""
    return (f"<h2>{escape(cv.label('profile'))}</h2>"
            f"<div class=\"profile\"><p>{escape(cv.profile)}</p></div>")


def _experience_block(cv: CV) -> str:
    if not cv.experience:
        return ""
    out = [f"<h2>{escape(cv.label('experience'))}</h2>"]
    for job in cv.experience:
        head = escape(job.employer)
        if job.period:
            head += f" &nbsp;<span class=\"meta\">{escape(job.period)}</span>"
        out.append(f"<div class=\"job\"><h3>{head}</h3>")
        if job.role or job.sector:
            sector = f" <span class=\"sector\">· {escape(job.sector)}</span>" if job.sector else ""
            out.append(f"<p class=\"role\">{escape(job.role)}{sector}</p>")
        if job.meta():
            out.append(f"<p class=\"meta\">{escape(job.meta())}</p>")
        out.append(_ul(job.duties))
        out.append("</div>")
    return "".join(out)


def _education_block(cv: CV) -> str:
    if not cv.education:
        return ""
    items = []
    for item in cv.education:
        year = f"{escape(item.year)} – " if item.year else ""
        where = f". {escape(item.where)}" if item.where else ""
        items.append(f"<li>{year}{escape(item.title)}{where}</li>")
    return f"<h2>{escape(cv.label('education'))}</h2><ul>{''.join(items)}</ul>"


def _skills_block(cv: CV) -> str:
    out = []
    if cv.skills:
        items = []
        for group in cv.skills:
            items.append(f"<li><span class=\"lead\">{escape(group.label)}</span>"
                         f" – {escape(group.text)}</li>")
        if cv.keywords:
            items.append(f"<li><span class=\"lead\">{escape(cv.label('keywords'))}</span>"
                         f" – {escape(cv.keywords)}</li>")
        out.append(f"<h2>{escape(cv.label('skills'))}</h2><ul>{''.join(items)}</ul>")
    if cv.personal_skills:
        out.append(f"<h2>{escape(cv.label('personal_skills'))}</h2>"
                   + _ul(cv.personal_skills))
    return "".join(out)


def _licences_block(cv: CV) -> str:
    if not cv.licences and not cv.licence_note:
        return ""
    out = [f"<h2>{escape(cv.label('licences'))}</h2>", _ul(cv.licences)]
    if cv.licence_note:
        out.append(f"<p class=\"small\">{escape(cv.licence_note)}</p>")
    return "".join(out)


def render_html(cv: CV, path: str | Path, *, designed: bool = False,
                title: str | None = None) -> Path:
    """Write a standalone HTML CV. ``designed=True`` uses the print stylesheet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    template = (TEMPLATES / "cv.html").read_text(encoding="utf-8")
    css = _style("cv-designed.css" if designed else "cv-ats.css")

    contact = cv.contact
    headline = f"<p class=\"headline\">{escape(contact.headline)}</p>" if contact.headline else ""
    subheadline = (f"<p class=\"subheadline\">{escape(contact.subheadline)}</p>"
                   if contact.subheadline else "")
    contact_line = " · ".join(x for x in (contact.location, contact.phone,
                                          contact.email) if x)
    notice = cv.privacy_notice or cv.label("gdpr")
    footer = (f"<p class=\"small notice\">{escape(notice)}</p>" if notice else "")

    html = template
    for token, value in {
        "{{LANG}}": cv.lang,
        "{{TITLE}}": escape(title or f"{contact.name} — curriculum vitae"),
        "{{STYLE}}": css,
        "{{NAME}}": escape(contact.name),
        "{{HEADLINE}}": headline + subheadline,
        "{{CONTACT}}": f"<p class=\"contact\">{escape(contact_line)}</p>",
        "{{PROFILE}}": _profile_block(cv),
        "{{EXPERIENCE}}": _experience_block(cv),
        "{{EDUCATION}}": _education_block(cv),
        "{{SKILLS}}": _skills_block(cv),
        "{{LICENCES}}": _licences_block(cv),
        "{{LANGUAGES}}": (f"<h2>{escape(cv.label('languages'))}</h2>"
                          + _ul([(x.name, x.level) for x in cv.languages],
                                lead=True) if cv.languages else ""),
        "{{AVAILABILITY}}": (f"<h2>{escape(cv.label('availability'))}</h2>"
                             + _ul(cv.availability) if cv.availability else ""),
        "{{FOOTER}}": footer,
    }.items():
        html = html.replace(token, value)
    path.write_text(html, encoding="utf-8")
    return path


def html_to_pdf(html_path: str | Path, pdf_path: str | Path | None = None) -> Path:
    """Convert an HTML file to PDF with WeasyPrint."""
    html_path = Path(html_path)
    pdf_path = Path(pdf_path) if pdf_path else html_path.with_suffix(".pdf")
    try:
        from weasyprint import HTML
    except Exception as exc:  # pragma: no cover - depends on the machine
        raise RuntimeError(
            "WeasyPrint is not installed, so the HTML route to PDF is unavailable.\n"
            "  pip install 'cvkit[html]'\n"
            "On Linux it also needs the system libraries for Pango and Cairo:\n"
            "  Debian/Ubuntu  sudo apt install libpango-1.0-0 libpangoft2-1.0-0\n"
            "  Fedora         sudo dnf install pango cairo\n"
            "  macOS          brew install pango libffi\n"
            f"(import error: {exc})"
        ) from exc
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    return pdf_path
