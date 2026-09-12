---
name: document-design
description: Judges and improves the visual quality of a printed CV — hierarchy, type scale, colour, black-and-white legibility, the two-page budget and an anti-generic checklist — against cv-kit's theme values and the built PDF. Use this when reviewing how a printed or printed-to-PDF CV looks, or when changing its typography, spacing, colour or page count.
---

# Document design for a printed CV

This skill judges one A4 portrait document that a person reads on paper or as a flat PDF. There is
no reflow, no scrolling, no hover, and the reader cannot enlarge the type. Every verdict below is
made on a built file, never on source code alone.

## Order of work

1. `pip install -e .`, then `cvkit build my-cv -o out`.
2. `cvkit qa out --expect-pages 2` for page count, printable-area overflow and the text layer.
3. `cvkit doctor` if no PDF appeared; install an export backend and rebuild.
4. Read the produced PDF page by page at 100 per cent, then print it in greyscale.
5. Report one verdict per check, naming the page and the exact value to change in `src/cvkit/theme.py`.

## Where the design values live

`src/cvkit/theme.py` holds `Palette`, `PageSpec`, `TypeScale` and the two presets that `preset()`
assembles. `ats` is single-column with tables and images disallowed; `designed` allows both. Change a
value there and rebuild — never restyle an exported document, and never fix a layout problem by
editing the generated `.docx`.

## 1. Hierarchy check

Three levels, and no more: the name, then the sections, then the entries inside them (employer, role,
period) and their body text. Verify that each level is visibly larger, bolder or better separated
than the one below it.

| Role | `designed` size | `ats` size |
|---|---|---|
| name | 19 pt bold (Georgia) | 19 pt bold (Arial) |
| headline | 11 pt | 11 pt |
| section heading | 10.5 pt | 10 pt |
| employer, role | 10 pt | 10 pt |
| subheadline, contact line | 9.5 pt | 9.5 pt |
| body, bullet | 9.2 pt | 10 pt body, 9.5 pt bullet |
| meta (dates, place, contract), small print | 8.5 pt | 9 pt meta, 8.5 pt small |

Sizes come from `TypeScale` in `src/cvkit/theme.py`; nothing in a builder hard-codes a point size.

Fail signals: a job title that is the same size and weight as its own bullets; an employer line that
does not stand out from the dates; a section heading smaller than the entry under it; the headline
larger than the name; more than three visual levels on one page.

## 2. Type-scale check

- Walk the scale in one direction: 19, 11, 10.5, 10, 9.5, 9.2, 8.5. Several neighbouring steps differ by less than one point, so size alone cannot carry the hierarchy — weight, colour and the spacing values (`section_before`, `section_after`, `entry_before`) must do the rest.
- Floor: nothing below 8.5 pt (`small`). Body text is 9.2 pt in `designed` and 10 pt in `ats`.
- Line and paragraph spacing are 1.06 and 1.10 in `ats`, 1.06 and 1.08 in `designed`. WCAG 1.4.8 asks for space-and-a-half and a mechanism to reach it, not that a document already uses those values [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html].
- Two font families at most: Arial only in `ats`; Calibri body with Georgia headings in `designed`.
- Body text is left aligned, never justified [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html].
- Reject a size that is not in the scale. If a value has to change, change `TypeScale` and rebuild.

## 3. Colour check

- `ats` uses black text on white with one grey rule (`ink`, `muted`, `primary`, `accent` are all `#000000`; `rule` is `#8C8C8C`). Add no colour to it.
- `designed` uses ink `#1F2933`, muted `#5B6770`, primary navy `#14395F`, accent teal `#0F6E6E`, rule `#C7D3DE`, shaded profile `#EEF3F7`, alternating table row `#F7F9FB` (`src/cvkit/theme.py`).
- Contrast: text needs at least 4.5:1 against its own background, and 3:1 for large-scale text, defined as at least 18 pt, or 14 pt when bold [https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html]. Check each pair that actually occurs, including muted text on the shaded profile block and text on the alternating table row. The muted grey and the teal are the pairs at risk.
- One accent colour, not a colour per section. Colour must never be the only carrier of a meaning: if a distinction vanishes when hue is removed, it is a defect.

## 4. Black-and-white check

Print the document in greyscale, or convert the PDF, and read that copy.

- The `ats` file is safe by construction: black, white and one grey.
- In `designed`, navy `#14395F` and teal `#0F6E6E` both convert to mid-greys, and the muted grey `#5B6770` sits in the same band. Anything distinguished only by hue — period text in teal, teal bullet markers, the shading behind the profile — must still read in grey.
- Light fills `#EEF3F7` and `#F7F9FB` are nearly white in print. Never place a heading or a required fact only inside a shaded block, and never rely on a fill to define a section.
- Confirm the acceptable floor in print: 8.5 pt is the smallest size the scale produces.
- Keep content clear of the sheet edge. `qa` fails a page whose content passes A4 height minus 14 mm (`src/cvkit/qa.py`); a stricter 10 mm trim safety margin is reported in the project's research brief and is UNVERIFIED here.
- Nothing critical in a header or a footer, at any size.

## 5. Two-page budget

- `DEFAULT_PLAN` (`src/cvkit/builder.py`) budgets two pages for `ats` and `designed`, one for `motivation`, two for `letters`. `cvkit qa out --expect-pages 2` asserts it; a mismatch is a `page-count` error.
- The budget is project policy, not a legal rule: no source in this repository establishes a legal page limit (UNVERIFIED).
- Cut in this order: bullets that carry no verifiable outcome; older roles reduced to one employer-named block with a date range and no duty list (`Job.duties` may be empty); duplicated keyword wording; a repeated contact line.
- Do not shrink body text below the scale, do not tighten the margins below `PageSpec`, do not move content into a header or footer, and do not add a third page. All four trade a layout problem for a parsing or legibility problem.

## 6. Anti-generic checklist

- [ ] No photo, icon, logo, chart, infographic, decorative border or QR code in an `ats`/`ats_en`/`portal` file; a photo belongs to the `designed` variant only, and the ATS presets forbid tables and images (`preset()`, `src/cvkit/theme.py`).
- [ ] No template furniture: no banner, no coloured name block, no sidebar, no timeline graphic, no skill bars or dots, no gauge, no "creative" two-column layout in a portal file.
- [ ] No rule, fill or highlight that carries no information. If deleting it changes nothing, delete it.
- [ ] No generic positioning language. `GENERIC_PHRASES` and `AGE_CUES` in `src/cvkit/model.py` are exactly the strings `validate` flags; replace them with a verifiable period, quantity or licence.
- [ ] No all-capital headings and no justified paragraphs.
- [ ] Measure a full body line: it should stay within 80 characters or glyphs. The criterion requires a mechanism to reach that width, not proof that the document already complies [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html].
- [ ] Every page still makes sense as a grey photocopy.
- [ ] The top third of page one answers three questions without searching: whose CV it is, which role it targets, and what verifiable experience backs that role.
- [ ] Any sentence that survives could not be pasted into a different person's CV unchanged.

## Reporting the result

Give one line per check: `pass` or `fail`, the page or PDF page number, and the exact change —
a value in `src/cvkit/theme.py` for layout, a field in the data file for content. Content edits
belong to the cv-engineering skill; this skill decides how the document looks and how much of it
fits on paper.

## Sources

- Repository files: `src/cvkit/theme.py`, `src/cvkit/qa.py`, `src/cvkit/builder.py`, `src/cvkit/model.py`, `src/cvkit/variants.py`.
- W3C WCAG 2.2, Understanding 1.4.3 Contrast (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- W3C WCAG 2.2, Understanding 1.4.8 Visual Presentation: https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html
