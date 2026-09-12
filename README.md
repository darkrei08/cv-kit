# cv-kit

Build a CV once, from structured data, and export every variant a real job search
needs: an ATS-plain document for portals, a designed document for printing, an
English version for cross-border applications, cover letters, and the plain text
that web forms ask you to paste.

One data model. One build command. No manual reformatting, no drifting copies.

```
src/               pip-installable package (cvkit)
docs/knowledge/    the research: CV standards, ATS constraints, print rules
skills/            agent skills, installable with `npx skills add`
examples/demo/     a synthetic CV that builds and self-checks in CI
```

## Why this exists

Most CV advice is about *what to write*. Almost nothing is about the part that
actually breaks: the same person needs four different documents, and hand-editing
four Word files produces four documents that disagree with each other. Worse, the
facts on a CV are usually verifiable — an employer can request the work-history
record from the public employment service — so drift is not just untidy, it is a
credibility risk.

`cv-kit` treats a CV as data plus a renderer:

- **Content lives in Python**, not in the document. Dates, employers, duties and
  licences are one source of truth.
- **Layout lives in code**, so the ATS variant cannot accidentally inherit a photo,
  a table or a colour that breaks parsing.
- **Exports are derived**, so a correction propagates to every variant at once.
- **Quality is checked by machine**: page count, forbidden fields, real text layer,
  layout overflow, and the absence of claims the record does not support.

## Requirements

| Component | Needed for | Windows | Linux | macOS |
|---|---|---|---|---|
| Python 3.10+ | everything | yes | yes | yes |
| `python-docx`, `pillow` | building the `.docx` | yes | yes | yes |
| `pymupdf` | quality checks and page counts | yes | yes | yes |
| Word + COM | best-fidelity PDF export | Windows only | no | no |
| `docx2pdf` | PDF export via Word | Windows | no | yes |
| LibreOffice | PDF export without Word | yes | yes | yes |
| `pandoc` | plain-text export for web forms | yes | yes | yes |
| WeasyPrint | HTML/CSS variant export | yes | yes | yes |
| `mmdc` (Mermaid CLI) | timeline diagrams | yes | yes | yes |

PDF export picks the first available backend automatically. See
[docs/cross-platform.md](docs/cross-platform.md) for the details and for what to
install on each system.

## Quickstart

```bash
pip install -e .            # from a clone of this repository

cvkit init my-cv            # scaffold a data file and asset folders
# edit my-cv/cv_data.py with your real facts
cvkit build my-cv -o out    # document variants + exports
cvkit qa out --expect-pages 2
```

Everything is driven by one data file. A minimal CV:

```python
from cvkit import CV, Contact, Job

cv = CV(
    contact=Contact(
        name="Maria Rossi",
        headline="Manutentrice elettrica",
        email="maria.rossi@example.com",
        phone="+39 000 000 0000",
        location="Bologna (BO), Italia",
    ),
    profile="Elettricista industriale con 12 anni di esperienza su quadri e "
            "impianti di automazione. Disponibile a turni e trasferte.",
    experience=[
        Job(
            period="03/2018 - 06/2025",
            employer="ACME Impianti S.r.l.",
            location="Bologna (BO)",
            role="Elettricista industriale",
            sector="Impianti elettrici industriali",
            contract="Tempo indeterminato, full time",
            duties=[
                "Manutenzione preventiva e correttiva su quadri di automazione.",
                "Lettura di schemi elettrici e ricerca guasti su impianti PLC.",
            ],
        ),
    ],
)
```

## What it produces

| Variant | Purpose | Constraints it respects |
|---|---|---|
| `ats` | portals and automatic screening | single column, Arial, black on white, no table, no image, real text layer |
| `designed` | printing and hand delivery | same facts, deliberate hierarchy, optional photo |
| `ats_en` | EURES, foreign employers | translated content, no photo |
| `motivation` | interviews, agency presentations | strongest verifiable arguments first |
| `letters` | speculative and advertised applications | one page, facts only, direct closing |
| `appendix` | portal and public-form fields | full contract list, dates, qualification codes |
| `guide` | the candidate's own instructions | channel by channel, print settings, checklist |

## Quality checks

`cvkit qa` is the part that keeps a CV honest and machine-readable:

- page count per variant, asserted against an expectation
- real text layer (a PDF that is an image fails every parser)
- no tables, no floating frames, no images in the ATS variant
- required fields present, forbidden fields absent (birth date, marital status,
  children, identity numbers, photo) in portal-facing variants
- content that would be clipped by the printable area
- claims that contradict the declared record

## Agent skills

`skills/cv-engineering` and `skills/document-design` teach an AI agent to build and
review a CV with this kit. Install for every agent on the machine:

```bash
npx skills add darkrei08/cv-kit --global
```

## Documentation

- [docs/knowledge/](docs/knowledge/) — the research behind every rule, with sources
- [docs/architecture.md](docs/architecture.md) — how data becomes a document
- [docs/cross-platform.md](docs/cross-platform.md) — operating-system specifics

## Licence

Code: [MIT](LICENSE). Knowledge documents in `docs/knowledge/`: [CC BY 4.0](LICENSE-docs).
