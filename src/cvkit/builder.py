"""Assemble documents from a CV.

Two shapes matter:

* the **master**: one file containing every part, each part starting on a new page.
  It is the thing a person edits and archives.
* the **single**: one part on its own, so a portal receives a two-page CV without
  a dossier cover page, without the reserved notes, and with its own page count.

Both are produced from the same builders, so they cannot disagree.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docx import Document

from .docx_kit import page_break, set_doc_defaults, setup_page
from .exporters import export_pdf, export_text
from .model import CV
from .theme import Preset
from .theme import preset as make_preset
from .variants import (
    build_appendix,
    build_ats,
    build_designed,
    build_letters,
    build_motivation,
    build_notes,
)

#: part name -> builder
PART_BUILDERS = {
    "ats": build_ats,
    "designed": build_designed,
    "motivation": build_motivation,
    "letters": build_letters,
    "appendix": build_appendix,
    "notes": build_notes,
}

#: part name -> preset used by that part
PART_PRESETS = {
    "ats": "ats",
    "designed": "designed",
    "motivation": "designed",
    "letters": "designed",
    "appendix": "designed",
    "notes": "designed",
}

#: The order a reader expects, and the default content of the master.
PART_ORDER = ("ats", "designed", "motivation", "letters", "appendix", "notes")

#: Files worth producing for a normal job search, and their expected length.
DEFAULT_PLAN = {
    "ats": {"export": ("docx", "pdf"), "pages": 2},
    "designed": {"export": ("docx", "pdf"), "pages": 2},
    "motivation": {"export": ("pdf",), "pages": 1},
    "letters": {"export": ("pdf",), "pages": 2},
    "appendix": {"export": ("pdf",), "pages": None},
}


@dataclass
class BuildResult:
    """Everything that was written, so a caller can check it afterwards."""

    files: dict[str, Path] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def add(self, kind: str, path: Path) -> Path:
        self.files[kind] = path
        return path


def new_document(preset: Preset | None = None, *, margins=None):
    p = preset or make_preset("ats")
    doc = Document()
    page = p.page
    if margins:
        page = type(page)(*margins, width_mm=page.width_mm, height_mm=page.height_mm)
    setup_page(doc.sections[0], page)
    set_doc_defaults(doc, p.palette, p.type.body, lang="it-IT")
    return doc


def set_metadata(doc, title: str, author: str, keywords: str = "") -> None:
    """Set the file properties.

    Without this, Word reports the generator as the author and exports an empty
    title: details a recruiter sees in the PDF properties before opening the file.
    OOXML caps these properties at 255 characters, so a long keyword line is
    truncated here — the document body keeps the full text, only the property is
    shortened, at a word boundary rather than mid-word.
    """
    properties = doc.core_properties
    properties.author = author
    properties.last_modified_by = author
    properties.title = title
    properties.subject = "Curriculum vitae"
    properties.comments = ""
    properties.category = ""
    properties.keywords = _clip(keywords, 255)
    properties.language = "it-IT"


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,;")


def build_master(cv: CV, path: str | Path, *, parts=PART_ORDER, include_notes: bool = True,
                 timeline_png: str | None = None, title: str | None = None,
                 author: str | None = None, findings=None,
                 translations: dict[str, CV] | None = None) -> Path:
    """One file with every part, each starting on a new page."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = new_document(make_preset("designed"))
    set_metadata(doc, title or f"Fascicolo curriculum vitae – {cv.contact.name}",
                 author or cv.contact.name, cv.keywords)
    builders = dict(PART_BUILDERS)
    if translations:
        for lang in translations:
            builders[f"ats_{lang}"] = build_ats
    first = True
    for part in parts:
        if part == "notes" and not include_notes:
            continue
        if not first:
            page_break(doc)
        if part.startswith("ats_") and translations:
            lang = part.split("_", 1)[1]
            builders[part](doc, translations[lang], make_preset("ats"))
        elif part == "motivation":
            builders[part](doc, cv, make_preset(PART_PRESETS[part]), None, timeline_png)
        elif part == "notes":
            builders[part](doc, cv, make_preset("designed"), findings)
        else:
            builders[part](doc, cv, make_preset(PART_PRESETS[part]))
        first = False
    doc.save(str(path))
    return path


def build_single(cv: CV, part: str, path: str | Path, *, timeline_png: str | None = None,
                 title: str | None = None, author: str | None = None,
                 findings=None) -> Path:
    """One part on its own, with its own page count."""
    if part not in PART_BUILDERS:
        raise ValueError(f"unknown part '{part}'; choose from {', '.join(PART_ORDER)}")
    path = Path(path)
    # Create the directory: a caller that names an output folder expects the file to
    # appear there, not a FileNotFoundError from three layers down.
    path.parent.mkdir(parents=True, exist_ok=True)
    preset = make_preset(PART_PRESETS[part])
    doc = new_document(preset, margins=_tight_margins(preset))
    set_metadata(doc, title or f"Curriculum vitae – {cv.contact.name}",
                 author or cv.contact.name, cv.keywords)
    if part == "motivation":
        build_motivation(doc, cv, preset, None, timeline_png)
    elif part == "notes":
        build_notes(doc, cv, preset, findings)
    else:
        PART_BUILDERS[part](doc, cv, preset)
    doc.save(str(path))
    return path


def _tight_margins(preset: Preset):
    """Single documents get slightly tighter margins than the master page."""
    if preset.name != "ats":
        return None
    return (14, 16, 14, 16)


def resolve_assets(cv: CV, base_dir: str | Path) -> list[str]:
    """Resolve relative photo and signature paths against a base directory.

    A data file usually declares ``assets/photo.jpg``, which only means something
    relative to the file that declares it. Without this, a document is built with the
    image silently missing: :func:`cvkit.model.validate` reports it as an error, but
    the resolution itself has to happen before the build.

    Returns the list of paths that could not be resolved anywhere.
    """
    base = Path(base_dir)
    missing: list[str] = []
    for attribute in ("photo", "signature"):
        value = getattr(cv.contact, attribute, "")
        if not value:
            continue
        path = Path(value)
        if path.is_absolute():
            # An absolute path is validated too: a file that exists but is not an
            # image must be reported, not passed on to fail later with a worse error.
            if path.exists():
                from .docx_kit import is_readable_image

                readable, why = is_readable_image(path)
                if not readable:
                    setattr(cv.contact, attribute, "")
                    missing.append(f"{value} ({why})")
            else:
                missing.append(value)
            continue
        for candidate in (base / path, base / path.name, path):
            if candidate.exists():
                from .docx_kit import is_readable_image

                readable, why = is_readable_image(candidate)
                if readable:
                    setattr(cv.contact, attribute, str(candidate.resolve()))
                else:
                    setattr(cv.contact, attribute, "")
                    missing.append(f"{value} ({why})")
                break
        else:
            missing.append(value)
    return missing


def build_all(cv: CV, out_dir: str | Path, *, translations: dict[str, CV] | None = None,
              timeline_png: str | None = None, plan: dict | None = None,
              exports: tuple[str, ...] = ("docx", "pdf"), findings=None,
              backend: str = "auto", prefix: str | None = None,
              asset_dir: str | Path | None = None) -> BuildResult:
    """Produce every file a job search needs, and report what was written.

    ``translations`` maps a language code to a fully translated CV; each one becomes
    an additional ATS file. ``plan`` overrides :data:`DEFAULT_PLAN`. ``asset_dir`` is
    the directory relative asset paths are resolved against, normally the folder that
    holds the data file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = plan or DEFAULT_PLAN
    stem = prefix or _stem(cv.contact.name)
    result = BuildResult()
    if asset_dir:
        result.notes.extend(
            f"asset not found: {name}" for name in resolve_assets(cv, asset_dir))
        for document in (translations or {}).values():
            resolve_assets(document, asset_dir)

    # The master, with and without the reserved notes.
    master = build_master(cv, out_dir / f"{stem}_CV_Master.docx",
                          timeline_png=timeline_png, findings=findings,
                          translations=translations)
    result.add("master", master)
    fascicolo = build_master(cv, out_dir / f"{stem}_CV_Fascicolo.docx",
                             include_notes=False, timeline_png=timeline_png,
                             translations=translations)
    result.add("fascicolo.docx", fascicolo)
    if "pdf" in exports:
        try:
            result.add("fascicolo", export_pdf(fascicolo, backend=backend))
        except RuntimeError as exc:
            result.notes.append(f"PDF export unavailable: {exc}")

    # One file per variant, so each platform gets exactly what it needs.
    for part, spec in plan.items():
        docx_path = build_single(cv, part, out_dir / f"{stem}_CV_{part.upper()}.docx",
                                 timeline_png=timeline_png, findings=findings)
        if "docx" in spec["export"]:
            result.add(f"{part}.docx", docx_path)
        if spec["export"] == ("docx", "pdf") and "pdf" not in exports:
            continue
        if "pdf" in spec["export"] and "pdf" in exports:
            try:
                result.add(part, export_pdf(docx_path, backend=backend))
            except RuntimeError as exc:
                result.notes.append(f"{part}: PDF export failed ({exc})")
        if "txt" in spec["export"]:
            result.add(f"{part}.txt", export_text(docx_path))

    if translations:
        for lang, translated in translations.items():
            path = build_single(translated, "ats",
                                out_dir / f"{stem}_CV_ATS_{lang.upper()}.docx")
            result.add(f"ats_{lang}.docx", path)
            if "pdf" in exports:
                try:
                    result.add(f"ats_{lang}", export_pdf(path, backend=backend))
                except RuntimeError as exc:
                    result.notes.append(f"ats_{lang}: PDF export failed ({exc})")
    return result


def _stem(name: str) -> str:
    """'Maria Grazia Rossi' -> 'Rossi_Maria_Grazia' (surname first, no spaces)."""
    parts = [p for p in name.replace(".", " ").split() if p]
    if not parts:
        return "CV"
    if len(parts) == 1:
        return parts[0]
    return "_".join([parts[-1]] + parts[:-1])
