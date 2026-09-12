# -*- coding: utf-8 -*-
"""Command line interface.

    cvkit doctor                      what this machine can do
    cvkit init my-cv                  scaffold a project
    cvkit build my-cv -o out          build every document and export it
    cvkit qa out                      check what was produced
    cvkit diagram my-cv -o out        render the career timeline
    cvkit html my-cv -o out           render the HTML variant

The contract with a project is one Python file, ``cv_data.py``, which defines ``cv``
(the CV), optionally ``cv_en`` (a translated CV) and optionally ``timeline`` (list of
``(label, description)`` pairs).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from . import exporters
from .builder import DEFAULT_PLAN, build_all, build_single
from .exporters import export_text
from .model import CV
from .qa import default_forbidden_tokens, qa_cv

DATA_FILE = "cv_data.py"

SCAFFOLD = '''# -*- coding: utf-8 -*-
"""CV data. This file is the single source of truth: the documents are generated
from it, so this is the only place where content is edited.
"""
from cvkit import CV, Contact, Education, Job, Language, Letter, SkillGroup

cv = CV(
    contact=Contact(
        name="Nome Cognome",
        headline="Titolo professionale mirato sull'annuncio",
        subheadline="Tre competenze chiave, separate da ·",
        email="nome.cognome@example.com",
        phone="+39 000 000 0000",
        location="Città (PR), Italia",       # forma breve: va nei portali
        address="",                          # indirizzo completo: solo versione curata
        personal={},                         # dati anagrafici: solo versione curata
        photo="",                            # assets/foto.jpg: solo versione curata
        signature="",                        # assets/firma.png: solo versione curata
        place_date="Città, mese anno",
    ),
    profile=(
        "Tre o quattro righe: dominio, anni verificabili, contesto tecnico, "
        "disponibilità. Nessun aggettivo su di sé: solo fatti."
    ),
    experience=[
        Job(
            period="03/2018 - 06/2025",
            employer="Azienda S.r.l.",
            location="Città (PR)",
            sector="Settore",
            role="Mansione svolta",
            contract="Tempo indeterminato, full time",
            duties=[
                "Prima responsabilità, con il numero o la macchina che la rende "
                "verificabile.",
                "Seconda responsabilità.",
            ],
        ),
    ],
    education=[
        Education(year="2011", title="Titolo o corso", where="Ente, città"),
    ],
    skills=[
        SkillGroup(label="Gruppo di competenze", text="Strumenti, macchine, "
                   "procedure concrete."),
    ],
    personal_skills=[
        "Autonomia operativa: un fatto, non un aggettivo.",
    ],
    licences=["Patenti e abilitazioni possedute."],
    licence_note="Precisazione onesta su cosa è stato esercitato e cosa no.",
    languages=[Language(name="Italiano", level="Madrelingua")],
    availability=["Disponibilità concreta, con decorrenza reale."],
    keywords="10-14 termini verificabili, separati da virgola",
    motivation=[
        ("1. Primo argomento verificabile", "Il fatto che lo sostiene."),
        ("2. Secondo argomento", "Il fatto che lo sostiene."),
    ],
    sectors=[("Area di lavoro", "Esperienza concreta", "Posizioni compatibili")],
    letter=Letter(
        subject="Candidatura - ruolo",
        paragraphs=["Primo paragrafo.", "Secondo paragrafo."],
        closing="Ringrazio per l'attenzione e porgo distinti saluti.",
        variants=[("Variante A - officina", ["Punto da mettere in evidenza."])],
    ),
    verification_notes=[
        ("Dato da verificare", "Come verificarlo e perché conta."),
    ],
)

# Facoltativo: una versione tradotta, che diventa un file ATS aggiuntivo.
# cv_en = CV(contact=Contact(name="Name Surname", headline="..."), lang="en", ...)

# Facoltativo: le tappe del percorso, per il diagramma della pagina motivazionale.
# timeline = [("1979", "Primo impiego come apprendista"), ("1997", "Specializzazione")]
'''


# ---------------------------------------------------------------------------
# Project loading
# ---------------------------------------------------------------------------
def load_project(directory: str | Path):
    """Import ``cv_data.py`` from a project directory."""
    directory = Path(directory).resolve()
    data_file = directory / DATA_FILE
    if not data_file.exists():
        raise SystemExit(f"no {DATA_FILE} in {directory}\n"
                         f"Run 'cvkit init {directory}' first.")
    spec = importlib.util.spec_from_file_location("cvkit_project_data", data_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cvkit_project_data"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    cv = getattr(module, "cv", None) or getattr(module, "CV_IT", None)
    if not isinstance(cv, CV):
        raise SystemExit(f"{data_file} must define a CV named 'cv'")
    translations = {}
    for attribute in dir(module):
        if attribute.startswith("cv_") and attribute not in {"cv_data"}:
            candidate = getattr(module, attribute)
            if isinstance(candidate, CV):
                translations[attribute.split("_", 1)[1]] = candidate
    timeline = getattr(module, "timeline", None)
    return directory, cv, translations, timeline


def _timeline_png(directory: Path, out_dir: Path, timeline, cv: CV) -> Path | None:
    from .diagrams import render_mermaid, timeline_source

    if not timeline:
        existing = out_dir / "timeline.png"
        return existing if existing.exists() else None
    source = timeline_source(timeline)
    try:
        return render_mermaid(source, out_dir / "timeline.png")
    except RuntimeError as exc:
        print(f"  timeline skipped: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_doctor(args) -> int:
    print(exporters.doctor())
    return 0


def cmd_init(args) -> int:
    directory = Path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    data_file = directory / DATA_FILE
    if data_file.exists() and not args.force:
        print(f"{data_file} already exists; use --force to overwrite")
        return 1
    data_file.write_text(SCAFFOLD, encoding="utf-8")
    (directory / "assets").mkdir(exist_ok=True)
    (directory / "assets" / ".gitkeep").write_text("", encoding="utf-8")
    print(f"created {data_file}")
    print(f"created {directory / 'assets'}")
    print("\nNext: edit the data file, then run:\n"
          f"  cvkit build {directory} -o out\n  cvkit qa out")
    return 0


def cmd_build(args) -> int:
    directory, cv, translations, timeline = load_project(args.directory)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = _timeline_png(directory, out_dir, timeline, cv)
    exports = ("docx",) if args.no_pdf else ("docx", "pdf")
    result = build_all(cv, out_dir, translations=translations or None,
                       timeline_png=str(png) if png else None, exports=exports,
                       backend=args.backend, prefix=args.prefix,
                       asset_dir=directory)
    if args.text:
        for name, spec in DEFAULT_PLAN.items():
            docx = result.files.get(f"{name}.docx")
            if docx:
                result.add(f"{name}.txt", export_text(docx))
    print(f"written to {out_dir}:")
    for kind, path in sorted(result.files.items()):
        print(f"  {path.name:44s} {kind}")
    for note in result.notes:
        print(f"  note: {note}", file=sys.stderr)
    return 0


def cmd_qa(args) -> int:
    target = Path(args.target)
    cv = None
    if args.directory:
        try:
            _, cv, _, _ = load_project(args.directory)
        except SystemExit:
            cv = None
    elif (target / DATA_FILE).exists():
        try:
            _, cv, _, _ = load_project(target)
        except SystemExit:
            cv = None

    files = {}
    if target.is_file():
        files[target.stem] = target
    else:
        for path in sorted(target.glob("*")):
            if path.suffix in {".pdf", ".docx"}:
                files[path.stem] = path
    if not files:
        print(f"nothing to check in {target}")
        return 1

    expect_pages = {}
    for path in files:
        if "ATS" in path.upper():
            expect_pages[path] = args.expect_pages or 2
    forbid = default_forbidden_tokens(cv) if cv else ()

    reports = qa_cv(cv, files, expect_pages=expect_pages, forbid_tokens=forbid)
    failed = 0
    for report in reports:
        print(report.text())
        if not report.ok:
            failed += 1
    print()
    print(f"{len(reports)} file(s) checked, {failed} with failures")
    return 1 if failed else 0


def cmd_diagram(args) -> int:
    directory, cv, _, timeline = load_project(args.directory)
    if not timeline:
        print(f"{DATA_FILE} does not define 'timeline'", file=sys.stderr)
        return 1
    from .diagrams import render_mermaid, timeline_source

    out = Path(args.output) / args.name
    out.parent.mkdir(parents=True, exist_ok=True)
    path = render_mermaid(timeline_source(timeline, title=args.title), out)
    print(f"written {path}")
    return 0


def cmd_html(args) -> int:
    directory, cv, translations, _ = load_project(args.directory)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    from .html_render import html_to_pdf, render_html

    made = []
    for lang, document in [("it", cv)] + list((translations or {}).items()):
        html_path = render_html(document, out_dir / f"cv-{lang}.html",
                                designed=args.designed)
        made.append(html_path)
        if not args.no_pdf:
            try:
                made.append(html_to_pdf(html_path))
            except RuntimeError as exc:
                print(f"  {lang}: {exc}", file=sys.stderr)
    for path in made:
        print(f"written {path}")
    return 0


def cmd_single(args) -> int:
    directory, cv, translations, timeline = load_project(args.directory)
    out = Path(args.output) / f"cv-{args.part}.docx"
    build_single(cv, args.part, out)
    print(f"written {out}")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cvkit", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="store_true", help="show version and exit")
    sub = parser.add_subparsers(dest="command")

    p_doctor = sub.add_parser("doctor", help="report which export backends are available")
    p_doctor.set_defaults(func=cmd_doctor)

    p_init = sub.add_parser("init", help="create a project with a data file")
    p_init.add_argument("directory")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_build = sub.add_parser("build", help="build every document and export it")
    p_build.add_argument("directory", nargs="?", default=".")
    p_build.add_argument("-o", "--output", default="out")
    p_build.add_argument("--no-pdf", action="store_true",
                         help="write the .docx files only")
    p_build.add_argument("--text", action="store_true",
                         help="also write the plain-text version for web forms")
    p_build.add_argument("--backend", default="auto",
                         choices=("auto", "word", "docx2pdf", "libreoffice"))
    p_build.add_argument("--prefix", default=None, help="override the file-name stem")
    p_build.set_defaults(func=cmd_build)

    p_qa = sub.add_parser("qa", help="check the produced files")
    p_qa.add_argument("target", nargs="?", default="out")
    p_qa.add_argument("--directory", default=None,
                      help="project directory, to read the expected forbidden fields")
    p_qa.add_argument("--expect-pages", type=int, default=None,
                      help="expected page count for ATS files (default 2)")
    p_qa.set_defaults(func=cmd_qa)

    p_diagram = sub.add_parser("diagram", help="render the career timeline")
    p_diagram.add_argument("directory", nargs="?", default=".")
    p_diagram.add_argument("-o", "--output", default="out")
    p_diagram.add_argument("--name", default="timeline.png")
    p_diagram.add_argument("--title", default=None)
    p_diagram.set_defaults(func=cmd_diagram)

    p_html = sub.add_parser("html", help="render the HTML variant")
    p_html.add_argument("directory", nargs="?", default=".")
    p_html.add_argument("-o", "--output", default="out")
    p_html.add_argument("--designed", action="store_true")
    p_html.add_argument("--no-pdf", action="store_true")
    p_html.set_defaults(func=cmd_html)

    p_single = sub.add_parser("single", help="build one part on its own")
    p_single.add_argument("part", choices=("ats", "designed", "motivation", "letters",
                                           "appendix", "notes"))
    p_single.add_argument("directory", nargs="?", default=".")
    p_single.add_argument("-o", "--output", default="out")
    p_single.set_defaults(func=cmd_single)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "version", False):
        from . import __version__
        print(__version__)
        return 0
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
