# -*- coding: utf-8 -*-
"""The document builders.

One function per part. Every one takes a :class:`~cvkit.model.CV` and a docx
document that already carries the styles of the chosen preset, and writes into it.
No function here knows anything about a specific person, and no function reads
configuration from anywhere except the preset it is given.
"""
from __future__ import annotations

import os

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt, RGBColor

from .docx_kit import (
    body_row, bullet, cell_shade, centred_image, clear_cell, ensure_cell_content,
    fixed_layout, header_row, keep_rows_together, make_style, page_break, para,
    para_border, para_shade, rich, tab_right,
)
from .model import CV, Finding, validate
from .theme import Preset
from .theme import preset as make_preset

# Default appendix heading; overridable through cv.labels.
APPENDIX_HISTORY_TITLE = "Elenco cronologico dei rapporti di lavoro"
APPENDIX_SECTORS_TITLE = "Aree di competenza e posizioni compatibili"
APPENDIX_CREDENTIALS_TITLE = "Patenti, abilitazioni e formazione"
MOTIVATION_TIMELINE_TITLE = "Percorso professionale in sintesi"


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def make_styles(doc, p: Preset) -> dict[str, str]:
    """Create the style set for a preset and return role -> style name."""
    palette, scale, key = p.palette, p.type, p.name
    names: dict[str, str] = {}

    def add(role: str, size: float, **kwargs):
        name = f"CVK{key}{role}"
        make_style(doc, name, size, font=kwargs.pop("font", palette.body_font), **kwargs)
        names[role] = name
        return name

    add("name", scale.name, bold=True, color=palette.primary, font=palette.head_font,
        after=1, line=1.0)
    add("headline", scale.headline, bold=True, color=palette.ink, after=0)
    add("subhead", scale.subheadline, italic=True, color=palette.muted, after=3)
    add("contact", scale.contact, color=palette.muted, after=0, line=1.10)
    add("section", scale.section, bold=True, color=palette.primary, allcaps=True,
        before=scale.section_before, after=scale.section_after, keep_next=True,
        font=palette.head_font)
    add("body", scale.body, color=palette.ink, after=2, line=scale.body_spacing)
    add("employer", scale.employer, bold=True, color=palette.primary,
        before=scale.entry_before, after=0, keep_next=True)
    add("role", scale.role, color=palette.ink if key == "ats" else palette.accent,
        bold=(key != "ats"), after=0, keep_next=True)
    add("meta", scale.meta, color=palette.muted, italic=(key != "ats"), after=0.5,
        keep_next=True)
    add("bullet", scale.bullet, color=palette.ink, after=scale.bullet_after, indent=5.0,
        hanging=3.6, line=1.06)
    add("small", scale.small, color=palette.muted, after=2, line=1.06)
    add("label", scale.meta, bold=True, color=palette.primary, after=0)
    add("title", scale.name, bold=True, color=palette.primary, font=palette.head_font,
        after=2)
    return names


def _section(doc, styles, p: Preset, title: str):
    paragraph = para(doc, title, style=styles["section"])
    para_border(paragraph, "bottom", p.palette.rule, 6, 2 if p.name == "ats" else 3)
    return paragraph


def _cell_section(cell, styles, p: Preset, title: str):
    paragraph = para(cell, title, style=styles["section"], before=3, after=2)
    para_border(paragraph, "bottom", p.palette.rule, 6, 3)
    return paragraph


def _labels(cv: CV, override: dict | None):
    def lookup(key: str) -> str:
        if override and key in override:
            return override[key]
        return cv.label(key)
    return lookup


# ---------------------------------------------------------------------------
# Variant: ATS-plain — for portals, parsers and e-mail attachments
# ---------------------------------------------------------------------------
def build_ats(doc, cv: CV, p: Preset | None = None, labels: dict | None = None):
    p = p or make_preset("ats")
    styles = make_styles(doc, p)
    L = _labels(cv, labels)

    _header(doc, cv, styles, p, short_location=True)
    if cv.profile:
        _section(doc, styles, p, L("profile"))
        para(doc, cv.profile, style=styles["body"])
    if cv.experience:
        _section(doc, styles, p, L("experience"))
        for job in cv.experience:
            _job(doc, job, styles, p, L("period"))
    if cv.education:
        _section(doc, styles, p, L("education"))
        _education(doc, cv.education, styles, p,
                   hide_year=cv.hide_education_years_in_ats)
    if cv.skills or cv.keywords:
        _section(doc, styles, p, L("skills"))
        for group in cv.skills:
            bullet(doc, group.text, style=styles["bullet"], lead=group.label,
                   marker_color=p.palette.marker)
        if cv.keywords:
            bullet(doc, cv.keywords, style=styles["bullet"], lead=L("keywords"),
                   marker_color=p.palette.marker)
    if cv.personal_skills:
        _section(doc, styles, p, L("personal_skills"))
        _bullets(doc, cv.personal_skills, styles, p)
    if cv.licences:
        _section(doc, styles, p, L("licences"))
        _bullets(doc, cv.licences, styles, p)
        if cv.licence_note:
            para(doc, cv.licence_note, style=styles["small"])
    if cv.languages:
        _section(doc, styles, p, L("languages"))
        for item in cv.languages:
            bullet(doc, item.level, style=styles["bullet"], lead=item.name,
                   marker_color=p.palette.marker)
    if cv.availability:
        _section(doc, styles, p, L("availability"))
        _bullets(doc, cv.availability, styles, p)
    notice = cv.privacy_notice or L("gdpr")
    if notice:
        paragraph = para(doc, notice, style=styles["small"], before=6)
        para_border(paragraph, "top", p.palette.rule, 6, 5)


# ---------------------------------------------------------------------------
# Variant: designed — for paper and hand delivery
# ---------------------------------------------------------------------------
def build_designed(doc, cv: CV, p: Preset | None = None, labels: dict | None = None):
    p = p or make_preset("designed")
    styles = make_styles(doc, p)
    L = _labels(cv, labels)
    width = p.page.usable_width_mm
    contact = cv.contact

    _designed_header(doc, cv, styles, p, width)

    if contact.personal:
        _section(doc, styles, p, L("personal"))
        _personal_grid(doc, contact.personal, p, width)

    if cv.profile:
        _section(doc, styles, p, L("profile"))
        paragraph = para(doc, cv.profile, style=styles["body"], after=0)
        para_shade(paragraph, p.palette.light)
        paragraph.paragraph_format.left_indent = Mm(3)
        paragraph.paragraph_format.right_indent = Mm(3)
        paragraph.paragraph_format.space_before = Pt(2)
        paragraph.paragraph_format.space_after = Pt(2)

    if cv.experience:
        _section(doc, styles, p, L("experience"))
        for job in cv.experience:
            heading = para(doc, job.employer, style=styles["employer"])
            tab_right(heading, width)
            heading.add_run("\t")
            run = heading.add_run(job.period)
            run.font.bold = False
            run.font.italic = True
            run.font.size = Pt(p.type.meta)
            run.font.color.rgb = RGBColor.from_string(p.palette.accent)
            if job.role:
                para(doc, job.role, style=styles["role"])
            if job.meta():
                para(doc, job.meta(), style=styles["meta"])
            for duty in job.duties:
                bullet(doc, duty, style=styles["bullet"], marker_color=p.palette.marker)

    _designed_tail(doc, cv, styles, p, width)
    _designed_footer(doc, cv, styles, p, width)


# ---------------------------------------------------------------------------
# Variant: motivation page
# ---------------------------------------------------------------------------
def build_motivation(doc, cv: CV, p: Preset | None = None, labels: dict | None = None,
                     timeline_png: str | None = None):
    p = p or make_preset("designed")
    styles = make_styles(doc, p)
    L = _labels(cv, labels)
    contact = cv.contact

    para(doc, L("motivation_title"), style=styles["title"])
    if contact.subheadline:
        para(doc, contact.subheadline, style=styles["subhead"])
    line = " · ".join(x for x in (contact.location, contact.phone, contact.email) if x)
    paragraph = para(doc, line, style=styles["contact"])
    para_border(paragraph, "bottom", p.palette.primary, 10, 4)

    for title, body in cv.motivation:
        para(doc, title, style=styles["section"], before=8, after=3)
        para(doc, body, style=styles["body"])

    if timeline_png and os.path.exists(timeline_png):
        _section(doc, styles, p, MOTIVATION_TIMELINE_TITLE)
        centred_image(doc, timeline_png, p.page.usable_width_mm)

    if cv.availability:
        _section(doc, styles, p, L("availability"))
        _bullets(doc, cv.availability, styles, p)
    if cv.licences:
        _section(doc, styles, p, L("licences"))
        _bullets(doc, cv.licences, styles, p)
        if cv.licence_note:
            para(doc, cv.licence_note, style=styles["small"])
    para(doc, " · ".join(x for x in (contact.name, contact.phone, contact.email) if x),
         style=styles["small"], align=WD_ALIGN_PARAGRAPH.CENTER, before=6)


# ---------------------------------------------------------------------------
# Variant: cover letters
# ---------------------------------------------------------------------------
def build_letters(doc, cv: CV, p: Preset | None = None, labels: dict | None = None):
    p = p or make_preset("designed")
    styles = make_styles(doc, p)
    contact = cv.contact
    letter = cv.letter
    if letter is None:
        return

    para(doc, cv.label("letters_title"), style=styles["title"])
    letter_head = " · ".join(x for x in (contact.address or contact.location,
                                         contact.phone, contact.email) if x)
    paragraph = para(doc, letter_head, style=styles["small"])
    para_border(paragraph, "bottom", p.palette.rule, 6, 4)
    if contact.place_date:
        para(doc, contact.place_date, style=styles["small"],
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    if letter.subject:
        para(doc, letter.subject, style=styles["label"], before=8, after=6)
    if letter.greeting:
        para(doc, letter.greeting, style=styles["body"])
    for block in letter.paragraphs:
        para(doc, block, style=styles["body"])
    if letter.closing:
        para(doc, letter.closing, style=styles["body"])
    _signature_block(doc, cv, styles, p)

    for title, focus in letter.variants:
        page_break(doc)
        para(doc, title, style=styles["headline"], after=4)
        for item in focus:
            bullet(doc, item, style=styles["bullet"], marker_color=p.palette.marker)


# ---------------------------------------------------------------------------
# Variant: appendix — for portal fields and public forms
# ---------------------------------------------------------------------------
def build_appendix(doc, cv: CV, p: Preset | None = None, labels: dict | None = None):
    p = p or make_preset("designed")
    styles = make_styles(doc, p)
    L = _labels(cv, labels)
    width = p.page.usable_width_mm

    para(doc, L("appendix_title"), style=styles["title"])
    if cv.contact.headline:
        para(doc, cv.contact.headline, style=styles["subhead"])
    line = " · ".join(x for x in (cv.contact.location, cv.contact.phone,
                                  cv.contact.email) if x)
    paragraph = para(doc, line, style=styles["contact"])
    para_border(paragraph, "bottom", p.palette.primary, 10, 4)

    if cv.experience:
        _section(doc, styles, p, APPENDIX_HISTORY_TITLE)
        widths = (28, 52, 45, width - 125)
        table = doc.add_table(rows=1, cols=4)
        table.autofit = False
        fixed_layout(table)
        header_row(table.rows[0].cells, widths,
                   ("Periodo", "Datore di lavoro", "Qualifica / mansione",
                    "Tipo di rapporto"), p.palette.primary)
        for index, job in enumerate(cv.experience):
            row = table.add_row()
            body_row(row.cells, widths,
                     (job.period,
                      " – ".join(x for x in (job.employer, job.location) if x),
                      job.role, job.contract or "non indicato"),
                     fill=p.palette.subtle if index % 2 else None)
        keep_rows_together(table)

    if cv.sectors:
        _section(doc, styles, p, APPENDIX_SECTORS_TITLE)
        widths = (38, 78, width - 116)
        table = doc.add_table(rows=1, cols=3)
        table.autofit = False
        fixed_layout(table)
        header_row(table.rows[0].cells, widths,
                   ("Area", "Esperienza e competenze", "Posizioni compatibili"),
                   p.palette.primary)
        for index, values in enumerate(cv.sectors):
            row = table.add_row()
            body_row(row.cells, widths, values,
                     fill=p.palette.subtle if index % 2 else None)
        keep_rows_together(table)

    if cv.licences or cv.education:
        _section(doc, styles, p, APPENDIX_CREDENTIALS_TITLE)
        _bullets(doc, cv.licences, styles, p)
        if cv.licence_note:
            para(doc, cv.licence_note, style=styles["small"])
        _education(doc, cv.education, styles, p, hide_year=False)

    if cv.contact.personal or cv.contact.address:
        _section(doc, styles, p, L("personal"))
        rows = {"Nome e cognome": cv.contact.name,
                "Residenza": cv.contact.address or cv.contact.location}
        rows.update(cv.contact.personal)
        for label, value in rows.items():
            bullet(doc, value, style=styles["bullet"], lead=label,
                   marker_color=p.palette.marker, lead_color=p.palette.accent)
        notice = cv.privacy_notice or L("gdpr")
        if notice:
            paragraph = para(doc, notice, style=styles["small"], before=6)
            para_border(paragraph, "top", p.palette.rule, 6, 4)


# ---------------------------------------------------------------------------
# Variant: verification notes — never sent to an employer
# ---------------------------------------------------------------------------
def build_notes(doc, cv: CV, p: Preset | None = None, findings: list[Finding] | None = None):
    p = p or make_preset("designed")
    styles = make_styles(doc, p)
    para(doc, "Note di verifica – non inviare", style=styles["title"])
    para(doc, "Dati da controllare prima di usare il CV in una candidatura",
         style=styles["subhead"])
    paragraph = para(doc, "Questa pagina non è inclusa nel PDF di stampa e non va mai "
                          "allegata a una candidatura.", style=styles["contact"])
    para_border(paragraph, "bottom", p.palette.primary, 10, 4)

    if findings:
        _section(doc, styles, p, "Controlli automatici")
        for finding in findings:
            bullet(doc, finding.message, style=styles["bullet"], lead=finding.code,
                   marker_color=p.palette.marker)
    if cv.verification_notes:
        _section(doc, styles, p, "Dati che devono essere verificati da te")
        for title, body in cv.verification_notes:
            para(doc, title, style=styles["role"])
            para(doc, body, style=styles["body"])


# ---------------------------------------------------------------------------
# Shared pieces
# ---------------------------------------------------------------------------
def _header(doc, cv: CV, styles, p: Preset, short_location: bool = True):
    contact = cv.contact
    para(doc, contact.name, style=styles["name"])
    if contact.headline:
        para(doc, contact.headline, style=styles["headline"])
    if contact.subheadline:
        para(doc, contact.subheadline, style=styles["subhead"])
    location = contact.location if (short_location or not contact.address) else contact.address
    line = " · ".join(x for x in (location, contact.phone, contact.email) if x)
    paragraph = para(doc, line, style=styles["contact"])
    para_border(paragraph, "bottom", p.palette.primary, 10, 4)
    return paragraph


def _job(doc, job, styles, p: Preset, period_label: str):
    para(doc, job.employer, style=styles["employer"])
    if job.role or job.sector:
        rich(doc, [(job.role, {}),
                   (" · " if job.sector else "", {"color": p.palette.muted}),
                   (job.sector, {"color": p.palette.muted})], style=styles["role"])
    chunks = [(period_label + " ", {"bold": True}), (job.period, {})]
    if job.contract:
        chunks += [(" · ", {"color": p.palette.muted}), (job.contract, {})]
    rich(doc, chunks, style=styles["meta"])
    for duty in job.duties:
        bullet(doc, duty, style=styles["bullet"], marker_color=p.palette.marker)


def _education(doc, education, styles, p: Preset, hide_year: bool):
    for item in education:
        if item.year and not hide_year:
            chunks = [(f"{item.year} – ", {"bold": True}), (item.title, {}),
                      (f". {item.where}" if item.where else "",
                       {"color": p.palette.muted})]
        else:
            chunks = [(item.title, {}),
                      (f". {item.where}" if item.where else "",
                       {"color": p.palette.muted})]
        rich(doc, chunks, style=styles["bullet"])


def _bullets(parent, items, styles, p: Preset):
    for item in items:
        bullet(parent, item, style=styles["bullet"], marker_color=p.palette.marker)


def _signature_block(doc, cv: CV, styles, p: Preset):
    signature = cv.contact.signature
    if signature and os.path.exists(signature):
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.add_run().add_picture(signature, width=Mm(26))
    para(doc, cv.contact.name, style=styles["small"], bold=True,
         align=WD_ALIGN_PARAGRAPH.RIGHT, color=p.palette.primary)


def _designed_header(doc, cv: CV, styles, p: Preset, width: float):
    contact = cv.contact
    photo = contact.photo if contact.photo and os.path.exists(contact.photo) else None
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    fixed_layout(table)
    left, right = table.rows[0].cells
    photo_column = 38.0 if photo else 0.0
    left.width = Mm(width - photo_column)
    right.width = Mm(photo_column)
    clear_cell(left)
    clear_cell(right)
    if photo:
        first = right.add_paragraph()
        first.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        first.paragraph_format.space_after = Pt(0)
        first.add_run().add_picture(photo, width=Mm(min(24.0, photo_column - 4)))
    para(left, contact.name, style=styles["name"], after=0)
    if contact.headline:
        para(left, contact.headline, style=styles["headline"])
    if contact.subheadline:
        para(left, contact.subheadline, style=styles["subhead"], after=0)
    para(left, contact.address or contact.location, style=styles["contact"], after=0)
    para(left, " · ".join(x for x in (contact.phone, contact.email) if x),
         style=styles["contact"], after=2)
    # A declared but missing photo leaves the right cell empty, and an empty cell
    # makes Word refuse the file. Fill it and let the quality checks report the
    # missing asset.
    return ensure_cell_content(table)


def _personal_grid(doc, personal: dict[str, str], p: Preset, width: float):
    pairs = list(personal.items())
    grid = doc.add_table(rows=0, cols=4)
    grid.autofit = False
    fixed_layout(grid)
    widths = (34.0, 48.0, 30.0, max(20.0, width - 112.0))
    for index in range(0, len(pairs), 2):
        row = grid.add_row()
        for cell, cell_width in zip(row.cells, widths):
            cell.width = Mm(cell_width)
        for column, (label, value) in enumerate(pairs[index:index + 2]):
            for cell, text, bold in ((row.cells[column * 2], label, True),
                                     (row.cells[column * 2 + 1], value, False)):
                paragraph = cell.paragraphs[0]
                paragraph.paragraph_format.space_after = Pt(1)
                run = paragraph.add_run(text)
                run.font.bold = bold
                run.font.size = Pt(9 if bold else 9.5)
                if bold:
                    run.font.color.rgb = RGBColor.from_string(p.palette.primary)
    return ensure_cell_content(grid)


def _designed_tail(doc, cv: CV, styles, p: Preset, width: float):
    """Two independent columns: skills and credentials left, history right."""
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    fixed_layout(table)
    left, right = table.rows[0].cells
    half = Mm(width / 2 - 2)
    left.width = half
    right.width = half
    clear_cell(left)
    clear_cell(right)

    if cv.skills:
        _cell_section(left, styles, p, cv.label("skills"))
        for group in cv.skills:
            rich(left, [(group.label, {"bold": True, "color": p.palette.accent}),
                        (" \u2014 ", {"color": p.palette.accent}),
                        (group.text, {})], style=styles["bullet"])
    if cv.licences:
        _cell_section(left, styles, p, cv.label("licences"))
        _bullets(left, cv.licences, styles, p)
        if cv.licence_note:
            para(left, cv.licence_note, style=styles["small"])

    if cv.education:
        _cell_section(right, styles, p, cv.label("education"))
        for item in cv.education:
            text = ". ".join(x for x in (item.title, item.where) if x)
            bullet(right, text, style=styles["bullet"], lead=item.year or None,
                   marker_color=p.palette.marker, lead_color=p.palette.primary)
    if cv.personal_skills:
        _cell_section(right, styles, p, cv.label("personal_skills"))
        para(right, " ".join(cv.personal_skills), style=styles["body"])
    if cv.languages or cv.availability:
        _cell_section(right, styles, p,
                      cv.label("languages") + " · " + cv.label("availability"))
        for item in cv.languages:
            bullet(right, item.level, style=styles["bullet"], lead=item.name,
                   marker_color=p.palette.marker, lead_color=p.palette.primary)
        _bullets(right, cv.availability, styles, p)
    return ensure_cell_content(table)


def _designed_footer(doc, cv: CV, styles, p: Preset, width: float):
    notice = cv.privacy_notice or cv.label("gdpr")
    if notice:
        declaration = cv.label("declaration")
        text = f"{declaration} {notice}" if declaration else notice
        paragraph = para(doc, text, style=styles["small"], before=3)
        para_border(paragraph, "top", p.palette.rule, 6, 5)
    signature = cv.contact.signature
    if (signature and os.path.exists(signature)) or cv.contact.place_date:
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        fixed_layout(table)
        left, right = table.rows[0].cells
        half = Mm(width / 2)
        left.width = half
        right.width = half
        if cv.contact.place_date:
            para(left, cv.contact.place_date, size=9.5, after=0)
        if signature and os.path.exists(signature):
            paragraph = right.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.add_run().add_picture(signature, width=Mm(26))
        para(right, cv.contact.name, size=9, bold=True, color=p.palette.primary,
             align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
        ensure_cell_content(table)
