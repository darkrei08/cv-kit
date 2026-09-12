# -*- coding: utf-8 -*-
"""cv-kit — build one CV as data and export every variant a job search needs.

Typical use::

    from cvkit import CV, Contact, Job, build_all, qa_cv

    cv = CV(contact=Contact(name="..."), experience=[Job(...)])
    result = build_all(cv, "out")

The pieces:

* :mod:`cvkit.model` — the data model and the validation rules
* :mod:`cvkit.theme` — page, type and colour presets
* :mod:`cvkit.variants` — one builder per document part
* :mod:`cvkit.builder` — assembly, and the master/single distinction
* :mod:`cvkit.exporters` — PDF and plain-text export, portable across systems
* :mod:`cvkit.qa` — automatic checks on the produced files
* :mod:`cvkit.diagrams` — Mermaid rendering for timeline graphics
* :mod:`cvkit.html_render` — the HTML/CSS route to PDF
"""
from .builder import (
    PART_ORDER, BuildResult, build_all, build_master, build_single, new_document,
    set_metadata,
)
from .model import (
    LABELS, CV, Contact, Education, Finding, Job, Language, Letter, SkillGroup,
    errors, validate,
)
from .theme import PALETTES, PAGES, TYPES, Palette, PageSpec, Preset, TypeScale
from .theme import preset as make_preset

__version__ = "0.1.0"

__all__ = [
    "CV", "Contact", "Education", "Job", "Language", "Letter", "SkillGroup",
    "Finding", "LABELS", "validate", "errors",
    "Palette", "PageSpec", "TypeScale", "Preset", "PALETTES", "PAGES", "TYPES",
    "make_preset",
    "build_all", "build_master", "build_single", "new_document", "set_metadata",
    "BuildResult", "PART_ORDER",
    "__version__",
]


def __getattr__(name: str):
    """Lazy access to the optional-dependency submodules.

    ``cvkit.qa`` needs PyMuPDF and ``cvkit.html_render`` needs WeasyPrint. Importing
    them on demand keeps the base package installable without either.
    """
    if name in {"qa", "exporters", "diagrams", "html_render"}:
        import importlib
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(name)
