# Architecture

## The one idea

A CV is data. The document is a rendering of that data. Everything else in this
repository follows from that sentence.

The alternative — editing four Word files by hand — produces four documents that
disagree with each other, and a CV is a document whose facts can be checked: an
employer can request the work-history record from a public employment service. Drift
is not untidiness, it is a credibility risk.

```
                     cv_data.py            (content: the only thing a person edits)
                          |
                          v
   +----------------------+----------------------+
   |                      |                      |
theme.py             variants.py             model.py
(page, type,         (one builder per       (dataclasses and the
 colour presets)      document part)         rules that make a CV usable)
   |                      |                      |
   +----------+-----------+----------------------+
              v
          builder.py            (assembly: one master file, and one file per variant)
              |
      +-------+--------+
      v                v
  document.docx     exporters.py  ----->  .pdf   (Word, docx2pdf or LibreOffice)
      |                                  .txt   (pandoc, or a built-in extractor)
      v                                  .html  (WeasyPrint)
   qa.py  (page count, text layer, forbidden fields, printable area)
```

## Modules, and what each one is allowed to know

| Module | Knows about | Must never know |
|---|---|---|
| `model.py` | dataclasses, section labels, validation rules | how anything is drawn |
| `theme.py` | numbers: margins, sizes, colours, spacing | a specific person or a specific document |
| `docx_kit.py` | python-docx and raw OOXML | a CV |
| `variants.py` | a `CV` object and a preset | a specific person |
| `builder.py` | assembly and file naming | page-level layout details |
| `exporters.py` | converting files, and which tool exists where | a CV |
| `qa.py` | measuring files and questioning claims | how a document was produced |
| `diagrams.py`, `html_render.py` | one alternative rendering each | the others |
| `guide.py` | the channel and print advice given to a candidate | the candidate's data |

Two consequences worth stating explicitly:

- **A variant cannot accidentally become non-compliant.** The ATS builder has no code
  path that inserts a photograph or a table, because the cells for those do not exist.
  Compliance is structural, not a review step.
- **A person cannot put content in a document.** There is nowhere to type it. Content
  lives in the data file or it does not exist.

## Master and single

Two shapes are produced from the same builders:

- **master** — every part in one file, one part per page. The thing a person edits and
  archives. It includes the reserved verification notes.
- **single** — one part alone, with its own page count and no dossier cover. This is
  what an employer receives.

They are built by the same functions, so they cannot disagree. The `include_notes`
switch is what keeps the reserved page out of the version that gets printed: those
notes are exactly the kind of thing that should never be sent by accident, and the
safest way to guarantee that is to generate a file that does not contain them.

## Presets

A preset is a palette, a page specification and a type scale. Two exist:

- `ats` — Arial, black and grey, no colour, no table, no image, tight margins.
- `designed` — Georgia headings over Calibri, one accent colour, two-column tail,
  roomer margins, photographs and personal details permitted.

Changing a preset changes every document that uses it. Adding a third is a matter of
adding one `Palette`, one `PageSpec` and one `TypeScale` in `theme.py`; no builder
changes.

## Quality checks are part of the build

`qa.py` is not a test suite for the package; it is a test suite for the *output*, and
it is meant to run on every build. It asserts:

1. the page count is inside the limit for that variant;
2. the PDF has a real text layer, because a scanned or outlined PDF is invisible to
   every parser whatever it looks like on screen;
3. no table, image or hidden text container in a portal variant;
4. no content outside the printable area;
5. no personal data in a portal variant, using the tokens derived from the model
   itself rather than a hand-written list;
6. no claim the model does not support (missing dates, roles, or duties; generic
   phrases; age cues).

Rule 5 is the interesting one: the list of forbidden strings is computed from
`Contact.personal` and `Contact.address`, so adding personal data automatically makes
it forbidden in the portal variants. A hand-maintained deny-list would rot.

## Extension points

| To do this | Change this |
|---|---|
| add a document part | a builder in `variants.py`, then register it in `PART_BUILDERS` |
| add a colour scheme | a `Palette`, `PageSpec`, `TypeScale` and an entry in `PRESETS` in `theme.py` |
| add a language | section labels in `LABELS`, plus a translated `CV` passed as `translations` |
| add an export format | a function in `exporters.py` and an entry in the plan |
| change a rule | a check in `model.validate` or `qa.py`; the knowledge documents explain why it exists |

## What is deliberately absent

- **No template files.** A `.docx` template is a document that drifts; the builders
  are code that can be reviewed and tested.
- **No database, no service, no network call at build time.** A CV build must work on
  a laptop with no connection.
- **No automatic translation.** The English variant is an authored translation because
  a machine translation of a job title is a fact that can become wrong.
- **No claims about parsers that cannot be verified.** The checks assert the properties
  a file must have; they do not promise that a specific commercial parser will behave.
