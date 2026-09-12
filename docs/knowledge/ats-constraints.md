# ATS constraints

This document is the contract between the CV a person reads and the CV software reads: what stops an applicant-tracking system (ATS) from extracting text, what does not, what a build pipeline can assert, how keywords are chosen, and how to test a file by hand. Read it before changing layout code: every rule maps to a check in `src/cvkit/qa.py`, so a layout change that defeats one of those checks is a regression.

## What breaks extraction

| Failure | What the parser gets | Source |
|---|---|---|
| Layout tables, columns, sidebars | Cell text in an order it cannot reconstruct. Greenhouse lists "complex resumes with tables, headers, and footers" and "a columned layout" as causes of an unsuccessful parse | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse) |
| Text boxes, floating frames | A missing field. In OOXML these are `w:txbxContent` and `w:framePr`; the QA pass fails on both | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse), `src/cvkit/qa.py:90-95` |
| Headers and footers | Named as a cause. Oracle documents the opposite for its own parser: "It can detect text in the header and footer". Keep name, phone and email in the body, which is safe under both | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse), [Oracle Taleo](https://docs.oracle.com/en/cloud/saas/taleo-enterprise/21b/otrec/candidate-management.html) |
| Images that carry text: logos, screenshots, infographics | No characters. Greenhouse lists "graphics, photos, or word art"; Workday advises using "resumes that don't have images or image-based styles" | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse), [Workday](https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/candidates/set-up-prospects-and-candidates/hdc1552497830785.html) |
| Scans, vector-outlined exports | A picture of letters: no text layer, so extraction returns nothing | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse) |
| Icon fonts | A code point with no assigned meaning: icon glyphs live in the Unicode Private Use Area, whose interpretation "is not specified by a character encoding standard". UNVERIFIED as a vendor statement | [Unicode private use](https://www.unicode.org/faq/private_use.html) |
| QR codes | An image, therefore no characters. UNVERIFIED as a vendor statement | UNVERIFIED |
| Letter-spaced text | Fragments: "the parser won't recognize the separate letters as a single word". Never apply character spacing to text that carries a keyword | [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse) |

## What does not break extraction

Rows marked UNVERIFIED rest on the absence of a documented cause, not on a vendor statement.

| Feature | Behaviour |
|---|---|
| Bold, italic, literal bullet characters | Oracle: "Resume Parsing has no impact on the formatting of a text (bold, italics, bullets)" ([Oracle Taleo](https://docs.oracle.com/en/cloud/saas/taleo-enterprise/21b/otrec/candidate-management.html)) |
| Text colour | Absent from Greenhouse's published cause list. UNVERIFIED as an explicit statement |
| Font family, including sans-serif | Absent from the cause list; Indeed still suggests sans-serif because "some ATS systems may struggle to read serif characters" while listing Times New Roman among its examples: a preference, not a rule ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv)) |
| Section headings in capitals | Both presets capitalise section headings (`src/cvkit/variants.py:51`); case is a character property, not a container. UNVERIFIED |
| Page breaks | They change page count, not characters; the real risks are the variant's target length and overflow (`src/cvkit/qa.py:119-129`, `src/cvkit/qa.py:143-146`). UNVERIFIED |

The ATS preset is black on white (`src/cvkit/theme.py:14-16`): a print decision, not a parsing one. Follow a rule that is free; never pay for one with a header, a text box or a column.

## What the pipeline asserts

| Check | Assertion | Implemented in |
|---|---|---|
| Page count | equals the declared expectation (2 for CV variants) | `src/cvkit/qa.py:143-146` |
| Real text layer | at least 400 extractable characters; below that the file is reported as an image or a vectorised export | `src/cvkit/qa.py:136-140` |
| No tables | zero in the `.docx` source of portal variants; a PDF cannot express a table to the checker, so the source is the file that gets asserted | `src/cvkit/qa.py:81-84` |
| No images | zero in the `.docx` source and on every PDF page | `src/cvkit/qa.py:85-86`, `src/cvkit/qa.py:131-133` |
| No text box or floating frame | `w:txbxContent` and `w:framePr` absent | `src/cvkit/qa.py:90-95` |
| Content inside the printable area | the lowest text block ends above A4 height minus the margin (14 mm default) | `src/cvkit/qa.py:107`, `src/cvkit/qa.py:119`, `src/cvkit/qa.py:124-129` |
| Forbidden fields absent | every declared personal value and configured token is searched in the extracted text; a hit is an error | `src/cvkit/qa.py:148-151`, `src/cvkit/qa.py:195-206` |
| Forbidden model fields | birth date, marital status, children, fiscal code, nationality, photo, age | `src/cvkit/model.py:180-183` |
| Keyword line | an empty keyword line warns; fewer than 10 terms raises `few-keywords` | `src/cvkit/model.py:270-278` |

For layout work:

- The 14 mm printable-area margin must equal the 14 mm ATS page margin (`src/cvkit/theme.py:78`, `src/cvkit/qa.py:107`). Change one, change both.
- Without PyMuPDF the page, text-layer and overflow checks are reported as skipped, not passed (`src/cvkit/qa.py:110-113`), so a green run needs the dependency present.
- The designed preset does use tables and images (`src/cvkit/theme.py:148-149`); never send that file to a parser.

## Keywords

- Use 10 to 14 comma-separated terms; fewer than 10 raises `few-keywords` (`src/cvkit/model.py:275-278`).
- Include only terms a record supports: an employer reference, certificate, licence, tool or practical test. A vacancy's requirement is evidence about the employer's wish, not about the candidate; Indeed's guidance is to mirror the advert only "purché corrisponda alle abilità reali", provided it matches real abilities ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv)).
- Put them where a parser reads: the headline under the contact block, the profile paragraph, the duty bullets and the competences list, where the keyword line renders as an ordinary bullet (`src/cvkit/variants.py:110-117`). Indeed describes the scan as top to bottom and left to right and warns against reordering blocks ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv)).
- Spell acronyms out beside the short form, and use the full standard job title and the company's legal name: Indeed warns that not every system recognises abbreviations, and Greenhouse lists incomplete job titles and company names without an identifying word among the causes of poor parsing ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv), [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)).
- Replace age cues with countable periods; the model warns on "40 years" and suggests the verifiable form, for example "17 years with one employer" (`src/cvkit/model.py:177`, `src/cvkit/model.py:254-257`).

## File format, by platform

| Platform | Accepts | Ceiling that matters |
|---|---|---|
| Indeed (job seeker) | Screening software generally prefers `.docx` ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv)). Accepted extensions and the reported 5 MB cap: UNVERIFIED |
| Greenhouse | `.doc`, `.docx`, `.pdf`, `.rtf`, `.txt`; uploads to 100 MB, but parsing stops above 2.5 MB | [Greenhouse formats](https://support.greenhouse.io/hc/en-us/articles/360052218132-Supported-formats-for-resumes-cover-letters-and-other-candidate-uploads), [Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse) |
| Workday | the resume attached to the application; results vary with "format and order of words" and image-based styles should be avoided. No published format list was confirmed | [Workday](https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/candidates/set-up-prospects-and-candidates/hdc1552497830785.html) |
| SAP SuccessFactors | Word, PDF or plain text; 5 MB default, raisable to 10 MB by the administrator | [SAP KBA 2081556](https://userapps.support.sap.com/sap/support/knowledge/en/2081556) |
| Oracle Taleo (legacy parse flow) | `.doc`, `.docx`, `.wpd`, `.txt`, `.rtf`, `.html`, `.pdf`, `.xls`, `.xlsx`, `.odt`; 100 KB per resume or the administrator's value | [Oracle Taleo](https://docs.oracle.com/en/cloud/saas/taleo-enterprise/21b/otrec/candidate-management.html) |
| LinkedIn | Microsoft Word or PDF; "we recommend a file size less than 2MB"; the four most recent resumes are kept | [LinkedIn Help](https://www.linkedin.com/help/linkedin/answer/a510363) |

- Send `.docx` when the portal accepts it and the advert is silent: it exposes paragraphs and headings as structure, and Indeed warns that an unusual format can stop the software reading the information ([Indeed Italia](https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv)). Send PDF when the platform or advert asks for it, and only with a real text layer.
- Stay under the tightest verified ceiling, LinkedIn's recommended 2 MB; Taleo's 100 KB default sits far below it, so assert against the ceiling the target platform declares. PDF/A is archival: none of the vendor pages verified here mentions PDF/A or tagged PDF as a parsing requirement (UNVERIFIED as a general statement).

## Test a file yourself

1. Select a line of the PDF with the mouse, copy it and paste it into a plain text editor. If nothing arrives, or you see boxes, there is no text layer: the file is a scan or an outlined export ([Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)).
2. Search the PDF (Ctrl+F) for one keyword, one year and your phone number: a miss means the term exists only inside a picture, and a phone number that appears only in the header or footer band belongs in the body ([Greenhouse parse](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)).
3. Count the pages, then run `cvkit qa out --expect-pages 2`.
4. Read the pasted text from top to bottom: if the order jumps between blocks, the document has columns.
