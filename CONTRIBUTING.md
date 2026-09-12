# Contributing

## Before you start

Two rules matter more than any style preference.

**1. No personal data in this repository.** It is public. The demonstration CV in
`examples/demo/cv_data.py` uses invented facts, and it must stay that way. If you add
an example, invent it. Names such as Giulia Bianchi, the address, the tax code and the
phone number in that file are placeholders, not real data — including the deliberately
invalid tax code, which exists so the checks have something to catch.

Run the guard before you push:

```bash
python scripts/check_no_pii.py .
```

For a private repository that generates a real CV, pass the real terms from a file
that is never committed:

```bash
export CVKIT_PII_TERMS="Surname,Firstname,Via Reale 1"
python scripts/check_no_pii.py .
```

**2. A claim needs a source.** Documentation in `docs/knowledge/` cites a primary
source for every non-obvious statement, or marks it `UNVERIFIED`. Adding a rule
without a source is worse than adding nothing: it makes the repository look
authoritative while spreading folklore. The same applies to code comments that justify
a number.

## Setting up

```bash
git clone https://github.com/darkrei08/cv-kit
cd cv-kit
python -m pip install -e ".[dev,qa,html]"
python -m pytest -q
python -m cvkit doctor
python examples/demo/build.py --no-pdf
```

## The checks you must run

```bash
python -m pytest -q                       # unit tests
python -m cvkit doctor                    # what this machine can do
python examples/demo/build.py --no-pdf    # documents build and self-check
python examples/demo/build.py             # the same, plus PDF pages (needs LibreOffice or Word)
python scripts/check_no_pii.py .          # nothing personal in the repository
```

If you touch a layout number in `theme.py`, run the full build and look at the page
counts the checks report. A change of one point of body size can add a page to a dense
CV, and the knowledge documents explain which value has which constraint.

## Style

- Python 3.10+, standard library first. Runtime dependencies stay at `python-docx` and
  `pillow`; everything else is an extra. Postponed annotations (`from __future__ import
  annotations`) and `X | None` type hints are used throughout.
- Comments explain *why*, never *what*. A comment that repeats the code is noise; a
  comment that records the constraint behind a number is the point of this repository.
- Keep line length at 100 characters (`ruff` is configured).
- User-facing document text is written in the language of the document, not in
  English by default. Code and documentation are in English.

## Adding a variant

1. Write the builder in `variants.py`. It takes `(doc, cv, preset, ...)` and writes
   into the document. It must not read global state or a specific person.
2. Register it in `PART_BUILDERS` and `PART_PRESETS` in `builder.py`.
3. Add it to `PART_ORDER` if it belongs in the master.
4. Add it to `DEFAULT_PLAN` with its exports and its page limit, or leave the limit
   `None` when the length is content-driven.
5. Add a test in `tests/test_build.py` that asserts the structural property that makes
   the variant valid — for a portal variant, that means no table and no image.
6. If the variant follows a rule from the research, cite it in the builder docstring
   and in `docs/knowledge/`.

## Adding a check

A check must be able to fail for a reason a person can act on, and it must not fire on
a legitimate document. A check that cries wolf is worse than no check, because it
teaches people to ignore the output. If a rule only applies to some variants, say so in
the code (`qa.is_portal_variant`) and test both sides.

## Reporting a problem

Open an issue with: the command you ran, the full output, your operating system, and
the output of `python -m cvkit doctor`. For a layout problem, attach the produced PDF —
the page geometry is most of the diagnosis.

## Licence

By contributing you agree that code is licensed under MIT and documentation under
CC BY 4.0, as described in `LICENSE` and `LICENSE-docs`.
