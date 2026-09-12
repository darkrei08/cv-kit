# Typography and print

This document justifies the numbers in `src/cvkit/theme.py`: type sizes, leading, spacing, margins, palette and photo geometry, for anyone about to change one. Sources are linked inline; values that are this repository's own choice, or that the brief behind these documents recorded as unverified, are labelled as such. WCAG addresses web content, so its figures serve here as thresholds, not as a claim of conformance.

## Type scale

From `theme.py` (`TypeScale`, lines 88–106); the HTML sheet mirrors the same values (`cv-ats.css`, lines 14–21). No authoritative source fixes before/after paragraph spacing, so the brief's values and this repository's stay unverified choices.

| Role | ATS | Designed | Note |
|---|---|---|---|
| Name | 19 pt bold | 19 pt bold | about 2× body; above WCAG "large", 18 pt or 14 pt bold [https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum] |
| Headline | 11 pt bold | 11 pt bold | the target role |
| Contact, subheadline | 9.5 pt | 9.5 pt | reference data |
| Section heading | 10 pt caps | 10.5 pt caps | never below body size |
| Employer, role | 10 pt | 10 pt | weight, not size, separates them |
| Meta: dates, place, contract | 9 pt | 8.5 pt | secondary line |
| Body | 10 pt | 9.2 pt | see the two-page trade-off |
| Bullet | 9.5 pt | 9.2 pt | 5 mm indent (`variants.py`, line 61), about 173 mm measure |
| Small | 8.5 pt | 8.5 pt | notices only |
| Leading | 1.06; body 1.10 | 1.06; body 1.08 | repository choice |
| Section spacing | 4 pt before, 2 pt after | 6 / 3 pt | repository choice |
| Entry spacing | 3 pt before, 2 pt after | 3 / 2 pt | repository choice |

- Floor: 9.5 pt for anything a reader must read, 8.5 pt for notices. Large print begins at 14 pt [https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum], so a 10 pt CV is not large print.
- WCAG 1.4.8 (AAA) asks only for a *mechanism* at 1.5 line spacing and 1.5 times paragraph spacing [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html]; nothing here is set at 1.5, deliberately.

## Fonts

- ATS is Arial (`theme.py`, lines 32–33). A neutral sans-serif is the safe default because the risks are substitution and low-resolution printing, not style. The UK National Careers Service advises "a clear font like Arial, Times New Roman or Calibri in size 11 or bigger" [https://nationalcareers.service.gov.uk/careers-advice/cv-sections].
- Arial is missing from some Linux systems; metric-compatible substitutes such as Liberation Sans keep its glyph advances, so pagination survives [https://wiki.archlinux.org/title/Metric-compatible_fonts]. The sheet also lists Helvetica and a generic sans-serif (`cv-ats.css`, line 14). Designed uses Calibri with Georgia headings (`theme.py`, lines 40–50) and is never parsed.

## Page, measure, alignment

| | ATS | Designed |
|---|---|---|
| Page, A4 per ISO 216 [https://www.iso.org/standard/36631.html] | 210 × 297 mm | same |
| Margins top/right/bottom/left | 14 / 16 / 14 / 16 mm | 15 / 17 / 15 / 17 mm |
| Usable width × height | 178 × 269 mm | 176 × 267 mm |

- Left-aligned, never justified: "never justify: rivers of white space in a narrow column" (`cv-ats.css`, lines 88–91); WCAG lists justification as failure pattern F88 [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html].
- Measure: 178 mm is 504.6 pt and Arial averages about 0.5 em per character, so a 10 pt body gives roughly 100 characters per line. Arithmetic on the font's average advance, not a measurement.
- WCAG's target is no more than 80 characters [https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html]: about 12.6 pt body here, or margins near 34 mm at 10 pt. The brief's 25/30 mm margins reach about 88. This kit accepts about 100, because a CV is bulleted fragments and Designed is the reading copy.

## Two pages versus readable type

- Two A4 pages is the convention for portal CVs and the maximum this kit asserts, not a legal rule.
- The brief's 11 pt at 1.15 leading with 20–30 mm margins costs roughly 25% more height per page (12.65 pt per line against 11.0 pt, plus about 10% more lines) and about 20% less usable area (155 × 257 mm against 178 × 269 mm) — roughly three pages for the same career. Arithmetic on those values, not a measurement.
- Resolution: two pages, a 10 pt body and 14–16 mm margins, with a code comment committing never to drop body text below 9.5 pt (`theme.py`, lines 76–77). The cost, plainly: 10 pt is below the brief's 11 pt and below the UK's "size 11 or bigger", so a size-mandated build must override it, and a reader who needs larger type is served by the plain-text export rather than the PDF.

## Colour

ATS is black, white and grey: colour does not break parsers — tables, text boxes and images do (`theme.py`, lines 8–10) — but the file is usually printed in black and white. Designed may use navy and teal.

- Never carry information by colour alone: WCAG 1.4.1 requires another visual means [https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html], and a hue change counts as a distinction only with 3:1 luminance contrast or more. A low-contrast rule may exist as decoration only: WCAG 1.4.11 applies 3:1 to graphics "required to understand the content" [https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html].
- Greyscale-print every variant before sending it.

| Pair, hex from `theme.py` | Ratio |
|---|---|
| ATS ink `#000000` on white | 21:1 |
| ATS muted `#333333` on white | 12.6:1 |
| ATS rule `#8C8C8C` on white | 3.4:1, decorative |
| Designed ink `#1F2933` on white | 14.8:1 |
| Designed muted `#5B6770` on white | 5.8:1 |
| Designed muted on `#EEF3F7` | 5.2:1 |
| Designed primary `#14395F` on white | 11.8:1 |
| Designed accent `#0F6E6E` on white | 6.0:1 |
| Designed rule `#C7D3DE` on white | 1.5:1, decorative only |

Ratios use the WCAG relative-luminance formula. Greyscale keeps luminance and discards hue: the accent is about 2.5:1 against body ink and the primary about 1.2:1, so both collapse to one grey and meaning pinned to them disappears on a mono printer.

## Print production

300 ppi at final size is the prepress standard for an image held in the hand [https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/resolution-specs-for-printing-images.html]; the unit is pixels per inch of the placed image, not printer dots per inch [https://www.whitewall.com/uk/magazine/guides/digital-image/image-quality-requirements-for-printing].

| Printed width | Pixels needed at 300 ppi | 413 × 531 px file gives |
|---|---|---|
| 24 mm | 283 px | 437 ppi |
| 35 mm | 413 px | 300 ppi |
| 40 mm | 472 px | 262 ppi |

- 35 × 45 mm is the travel-document proportion: ICAO Doc 9303 Part 3, "Submitted portraits should be 45.0 mm x 35.0 mm" [https://www.icao.int/sites/default/files/publications/DocSeries/9303_p3_cons_en.pdf]. Italy's passport sheet allows 35–40 mm width, face 70–80% of the frame [https://www.poliziadistato.it/statics/10/fotografia_passaporto_web.pdf], so 35 mm is a convention, not one legal number.
- `prepare_photo` crops to that ratio at 413 × 531 px, upscales with Lanczos, sharpens and writes 300 dpi (`docx_kit.py`, lines 308–330). Enlargement creates no detail.
- Why 24 mm is acceptable and 40 mm is not: at 24 mm the file is oversampled at 437 ppi, so interpolation is invisible; at 40 mm it lands at 262 ppi, below the standard, and the widening is what the reader sees. The Designed header reserves 38 mm and prints min(24 mm, column − 4 mm) (`variants.py`, lines 422–431), not the "30–35 mm wide" of its own docstring (`docx_kit.py`, lines 312–313).
- RGB versus CMYK: keep RGB, convert only when an offset shop names a press condition, because paper is subtractive and the gamuts differ [https://www.hp.com/us-en/tech-takes/printing/comparison/print-basics-rgb-vs-cmyk.html] [https://www.fespa.com/en/news-media/are-there-advantages-using-an-rgb-workflow-over-an-cmyk-workflow/]. ATS has nothing to convert, and Designed loses no meaning in greyscale, which is why that check matters more than the conversion.
- Trim: keep everything 10 mm or more inside it. The kit does this by geometry, through the 14–16 mm margins, and `qa.py` errors when a block reaches the printable boundary (`qa.py`, lines 126–135). A given printer's non-printable edge is a device property: UNVERIFIED as a universal figure.
- Duplex: two CV pages are one sheet; print a cover letter single-sided when it is handed over on its own.
- Paper: 80 g/m² is ordinary office stock, 90–100 g/m² uncoated suits a copy placed in a hand. Grammage is the ISO 536 quantity [https://www.iso.org/standard/77583.html]; the weight, like avoiding coated stock, is convention.

## PDF specifics

- Real text layer always: a scanned or vector-outlined PDF fails every parser, and `qa.py` errors below 400 extractable characters (`qa.py`, lines 144–147).
- Embedded fonts: required by PDF/A [https://pdfa.org/resource/iso-19005-1-pdf-a-1/ returned HTTP 403 to automated fetching] and needed in practice, because a file naming Arial without embedding it is re-laid-out with a substitute, so the page count holds only while that substitution is metric-exact.
- Metadata: set Title and Author (`builder.py`, lines 87–104), since Word otherwise names the generator as author and leaves the title empty. Strip unintended DOCX author and company fields with the Document Inspector [https://support.microsoft.com/en-gb/office/inspect-document-b0088a7a-d482-4b87-b762-7c94c7c71e23]; a stale employer there discloses what the body withholds.
- PDF/A only on request: -1b is Level B (visual reproduction, embedded fonts, device-independent colour), -2u adds Unicode mappings, -1a and -2a add tagging [https://pdfa.org/resource/iso-19005-pdfa/]. No ATS source requires PDF/A, and -1b without Unicode mappings can extract worse than a plain PDF. Platform caps are 5 MB (Indeed) and 2 MB (LinkedIn).

## Accessibility

- Contrast: 4.5:1 for normal text, 3:1 for large text, meaning at least 18 pt or 14 pt bold [https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum].
- Resize: 200% without loss of content [https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html]; a fixed-layout PDF zooms as a whole and the HTML export scales with the browser, so verify reflow.
- Never rely on colour alone [https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html], containers a parser cannot see, headers or footers (parsers and screen readers skip them; Microsoft says not to put important information there [https://support.microsoft.com/en-us/office/make-your-word-documents-accessible-to-people-with-disabilities-d9bf3683-87ac-47ea-b91a-78dcacb3c66d]), images of text or icon-font glyphs, or layout tables. ATS enforces the structural half (`model.py`, lines 179–183; `qa.py`, lines 82–96), and any image reaching HTML or a tagged PDF needs alt text.
