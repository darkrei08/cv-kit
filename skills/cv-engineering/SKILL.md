---
name: cv-engineering
description: Builds and checks a CV from structured cv-kit data — reading the data file before editing anything, keeping all content in Python, running the build and the quality checks, applying the forbidden-fields rule to portal variants, marking unsupported claims for verification instead of publishing them, and recovering when the PDF backend is missing. Use this when a CV, cover letter or portal variant has to be created, edited, rebuilt or validated with cv-kit.
---

# CV engineering with cv-kit

A cv-kit CV is one Python model rendered into every variant: work on the data, never on the
document. A fact corrected inside an exported `.docx` or PDF disappears at the next build, and the
variants start disagreeing with each other.

## Order of work

1. **Read the data file before editing anything.** `cvkit build` reads the module that constructs `CV(...)`; so must you. `cvkit init <name>` scaffolds it as `<name>/cv_data.py`. Read it in full, then read the source record behind each claim (work-history record, licence, certificate).
2. **Install.** `pip install -e .` from a clone of this repository. The quality checks additionally need PyMuPDF: `pip install 'cvkit[qa]'`.
3. **Edit the model, never the output.** Content belongs to the dataclasses in `src/cvkit/model.py`.
4. **Build.** `cvkit build my-cv -o out` writes a master plus one file per part — `ats`, `designed`, `motivation`, `letters`, `appendix`, `notes` (`DEFAULT_PLAN`, `src/cvkit/builder.py`).
5. **Check.** `cvkit qa out --expect-pages 2`.
6. **Fix the model and rebuild** until the checks pass. The derived files are overwritten on every build; there is nothing in them worth preserving.

## Fields that exist

| Dataclass | Fields |
|---|---|
| `Contact` | `name`, `headline`, `subheadline`, `email`, `phone`, `location`, `address`, `personal`, `photo`, `signature`, `place_date` |
| `Job` | `period`, `employer`, `role`, `sector`, `location`, `contract`, `duties` |
| `Education` | `title`, `year`, `where` |
| `SkillGroup` | `label`, `text` |
| `Language` | `name`, `level` |
| `Letter` | `subject`, `greeting`, `paragraphs`, `closing`, `variants` |
| `CV` | `contact`, `profile`, `experience`, `education`, `skills`, `personal_skills`, `licences`, `licence_note`, `languages`, `availability`, `keywords`, `motivation`, `sectors`, `letter`, `lang`, `hide_education_years_in_ats`, `labels`, `privacy_notice`, `verification_notes` |

Two defaults matter. `hide_education_years_in_ats` is `True`: a schooling year is an age cue with no
selection value. `lang` selects the section titles from the `LABELS` dictionary, so change labels
through `labels`, not by renaming a section in the output.

## The forbidden-fields rule for portal variants

Portal-facing variants are `ats`, `ats_en` and `portal`. They must not carry `birth`, `nascita`,
`marital`, `coniug`, `figli`, `children`, `codice fiscale`, `fiscal`, `nazionalita`, `nationality`,
`photo`, `foto`, `age`, `eta` (`PERSONAL_FORBIDDEN_IN_ATS`, `src/cvkit/model.py`).

- Such data lives in `Contact.personal`, `Contact.address`, `Contact.photo` and `Contact.signature`. `build_ats` never renders them; the designed variant and the appendix do (`src/cvkit/variants.py`).
- `validate(cv, variant="ats")` reports `personal-data-in-portal-variant` and `photo-in-portal-variant`; `qa_cv` adds `personal-data-present`; and `default_forbidden_tokens(cv)` turns every personal-block value of six or more characters, plus the full address, into `forbidden-token` checks against the produced PDF (`src/cvkit/qa.py`).
- Check per variant, not once: the designed file is allowed exactly what the portal file is not.
- A photo, a table, a text box or an image in a portal file is a parsing defect, not a style choice. Indeed's own ATS guidance tells candidates to avoid headers, footers, symbols, logos and images containing text [https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv].

## A claim the source record does not support

- Do not publish it, and do not close the gap by guessing. Record it in `CV.verification_notes` as `(title, body)` pairs: they are rendered only in the `notes` part, whose heading states that the page must never be attached to an application, and never in the portal or designed variants (`src/cvkit/variants.py`).
- Do not promote a vacancy's requirement into experience. A skill the advert asks for is not evidence that the candidate has it.
- Never invent a quantity, a machine model, a date or a licence status. If the source marks a value uncertain, keep the uncertainty visible in the note.
- `validate` flags unverifiable positioning with `generic-phrase` and `age-cue`. The sanctioned replacement for an age cue is a verifiable period, for example "17 years with one employer" (`src/cvkit/model.py`).

## Interpreting `cvkit qa` failures

`cvkit qa` runs `validate(cv, variant)` over the model and `inspect_docx` / `inspect_pdf` over the
files. Fix every error, review every warning.

| Code | Meaning and fix |
|---|---|
| `missing-name`, `missing-email`, `bad-email`, `no-experience`, `job-without-dates`, `job-without-role` | Model errors: the entry is unusable as written |
| `page-count` | The file does not have the page count passed to `--expect-pages` |
| `content-outside-printable-area` | A block ends below A4 height minus the 14 mm margin; shorten it or tighten the page spec |
| `no-text-layer` | Fewer than about 400 extractable characters: the PDF is a scan or its text is vectorised, and no parser can read it |
| `table-in-portal-variant`, `image-in-portal-variant` | A table or image reached an `ats`/`ats_en`/`portal` file; remove it |
| `hidden-text-container` | A Word text box or floating frame, invisible to most parsers |
| `forbidden-token` | Text from `default_forbidden_tokens(cv)` reached this file |
| `personal-data-in-portal-variant`, `personal-data-present`, `photo-in-portal-variant` | Personal data or a photo is on a portal path; move it to `Contact.personal` or keep it out |
| `too-many-duties` | More than five bullets for one job; four is a practical maximum |
| `profile-too-long` | Over 130 words; the check asks for under 130 words, four lines |
| `no-keywords`, `few-keywords` | Fewer than ten keyword terms; ten to fourteen supported terms is the useful range |
| `generic-phrase`, `age-cue` | Unverifiable positioning; replace with a verifiable fact |
| `missing-headline`, `missing-phone`, `missing-profile`, `empty-verification-note` | Warnings about an incomplete entry |
| `SKIP ...` | The check did not run, usually because PyMuPDF is absent. A skip is not a pass: install `cvkit[qa]` and re-run |

## When the PDF backend is missing

- PDF export tries Word, then `docx2pdf`, then LibreOffice, in that order (`_BACKEND_ORDER`, `src/cvkit/exporters.py`).
- With none of them available the export raises `RuntimeError: no PDF backend worked`, and `build_all` records it in `BuildResult.notes` instead of failing: the `.docx` files exist, the PDFs do not.
- Diagnose with `cvkit doctor` (implemented by `exporters.doctor()`): it reports Word, `docx2pdf`, LibreOffice, pandoc, `python-docx`, pillow, PyMuPDF and WeasyPrint.
- Install LibreOffice — Windows `winget install TheDocumentFoundation.LibreOffice`; macOS `brew install --cask libreoffice`; Debian `sudo apt install libreoffice-writer`; Fedora `sudo dnf install libreoffice-writer`; Alpine `apk add libreoffice-writer`; Arch `sudo pacman -S libreoffice-fresh`.
- Or force the backend that does exist: `export_pdf(docx, backend="libreoffice")`.
- LibreOffice pagination is "very close but not guaranteed identical to Word" (`src/cvkit/exporters.py`), so always re-run `cvkit qa` on the PDF that was actually produced.

## Sources

- Repository files: `src/cvkit/model.py`, `src/cvkit/qa.py`, `src/cvkit/variants.py`, `src/cvkit/builder.py`, `src/cvkit/exporters.py`, `src/cvkit/theme.py`, `README.md`.
- Indeed Italia, ATS guidance (file format, headers/footers, symbols, logos, images containing text): https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv
