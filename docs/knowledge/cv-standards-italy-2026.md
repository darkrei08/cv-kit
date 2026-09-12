# CV standards and application channels — Italy, 2026

This is the Italian lane of cv-kit's research base: the section order and names Italian recruiters and portals expect, the personal data to omit for legal reasons, what each live Italian channel requires, how a portal-compiled CV differs from the CV a public competition expects, and why hiring incentives never belong on a candidate document. Read it when configuring the Italian data model, writing its renderer, or reviewing a generated variant. Conventions are labelled as conventions; anything not confirmed against a primary source is marked UNVERIFIED and left unresolved.

## Summary for the impatient

| Decision | Rule | Why |
|---|---|---|
| Section order | Contact → professional profile → experience → education → skills/certifications → languages | Screening software reads top to bottom; reordering blocks breaks parsing [https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv] |
| Personal data | Omit photo, birth date, marital status, children, nationality, health, birth place, codice fiscale | Data minimisation [https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A32016R0679] plus the ban on discrimination in access to employment [https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-07-09;216~art3] |
| Layout | One column; no tables, sidebars, headers, footers or images | Complex formatting blocks correct interpretation [https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv] |
| Public sector | Compile the CV in the portal; the bando wins | [https://www.inpa.gov.it/faq-domande-e-risposte/] |
| Incentives | Never on the CV | The benefit is the employer's and rests on facts the candidate does not hold [https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A03291&art.dataPubblicazioneGazzetta=2026-06-27&art.flagTipoArticolo=0&art.idArticolo=3&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=0&art.versione=1] |
| Length | 2 pages | Convention, not law — UNVERIFIED |
| Before export | Real text layer; no scan, no vector outlines | [https://support.indeed.com/hc/en-gb/articles/4408783727629-Uploading-a-CV-file-to-your-profile] |

## 1. Section order and names

Working order. The exhaustive sequence is this project's convention; no primary source located fixes a legally required order — UNVERIFIED.

| # | Italian heading | What it holds |
|---|---|---|
| 1 | Dati di contatto | Name, phone, email, city; one role-targeted headline. No photo, birth data or full address |
| 2 | Profilo professionale | Three to four lines, only supported claims |
| 3 | Esperienza lavorativa | Reverse chronological; employer, title, dates, contract type as body text, never in a text box |
| 4 | Istruzione e formazione | Highest qualification; leave graduation years off — a year is an age cue |
| 5 | Competenze e certificazioni | 10–14 plain-text keywords; licences with status and expiry |
| 6 | Lingue | "Italiano — madrelingua"; CEFR levels only with evidence |

What *is* sourced is the principle behind the order: the document is read top to bottom, each section must be immediately identifiable from its heading, and contact/identity, experience with dates-employer-duties, and education/certifications are the recognised blocks [https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv]. Layout follows parsing: no tables, columns, sidebars, headers, footers, images, icons or logos carrying important content; no scanned or photographed CV; no two-column layout [https://support.indeed.com/hc/en-gb/articles/4408783727629-Uploading-a-CV-file-to-your-profile].

## 2. What to omit, and why

| Field | Rule | Basis |
|---|---|---|
| Birth date, age | Omit | Equal treatment covers access to employment including selection criteria and hiring conditions, and age is a protected ground [https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-07-09;216~art3] |
| Nationality | Omit | The same article lists nationalità among the protected grounds [https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-07-09;216~art3] |
| Health, disability | Omit unless legally required or an accommodation is requested | Article 9 GDPR special category; the supervisory authority's provisions cover job candidates including CVs sent spontaneously [https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9124510] |
| Photo | Omit from the standard CV; a photo version only for a confirmed front-of-house case | No Italian statute located requiring or banning it — UNVERIFIED. It discloses protected characteristics [https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-07-09;216~art3] and degrades parsing [https://support.indeed.com/hc/en-gb/articles/4408783727629-Uploading-a-CV-file-to-your-profile] |
| Marital status, children | Omit | Not job-relevant; no statute located specifically banning the question — UNVERIFIED; the rule rests on minimisation [https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A32016R0679] |
| Codice fiscale, birth place | Omit | No application-stage purpose [https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A32016R0679] |
| Everything | Include only what the advert requires | Article 5(1)(c) GDPR: adequate, relevant and limited to what is necessary [https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A32016R0679] |

A portal may legitimately hold identity data the CV must not carry: on inPA the registry block is pre-filled from the identity provider and is not editable by the user [https://www.inpa.gov.it/faq-domande-e-risposte/]. Do not confuse what a portal already knows with what belongs on the document.

## 3. Live channels and what each requires

| Channel | Status | Requirement |
|---|---|---|
| ClicLavoro Basilicata | Live | SPID to publish a CV and enter the region's Avvisi Pubblici [https://lavoro.regione.basilicata.it/servizio/cliclavoro-basilicata/] |
| CPI (public employment centres) | Live | Registration at the CPI for the area of residence and release of the DID; orientation, short training, matching; EURES advisers operate in many CPIs [https://www.lavoro.gov.it/sportello-unico-digitale/ricerca-di-occupazione/ricerca-di-occupazione-e-assistenza-centri-limpiego]. Basilicata offices publish per-office contacts [https://www.agenziaregionalelab.it/centri-per-limpiego/] |
| inPA | Live | SPID, CIE, CNS or eIDAS; the CV is compiled inside the portal, incomplete sections are flagged, a PDF can be downloaded [https://www.inpa.gov.it/faq-domande-e-risposte/]. The platform rests on Art. 35-ter D.Lgs. 165/2001 [https://www.inpa.gov.it/wp-content/uploads/2024/07/dfp_52963_Circolare_Portale_inPA_1_7_2022_signed.pdf] |
| EURES + Europass | Live, re-based | Jobseeker accounts closed on 31 March 2025; from 1 April 2025 Europass is the jobseeker platform, and a profile must be linked and shared with EURES to be visible to employers and EURES advisers [https://eures.europa.eu/looking-work-europe-heres-how-changes-eures-portal-affect-you-2025-03-18_it]. The "explicit consent" wording is UNVERIFIED [https://eures.europa.eu/eures-services/help-and-support_it] |
| Indeed Italia | Live | .doc, .docx, .txt, .rtf, and PDF which is auto-converted [https://www.indeed.com/career-advice/resumes-cover-letters/how-to-upload-resume-to-indeed]; one file at a time, replaced on upload [https://support.indeed.com/hc/en-ca/articles/11314976176141-FAQs-Creating-Uploading-and-Managing-a-Resume-File]; screening software generally prefers .docx [https://it.indeed.com/guida-alla-carriera/cv-lettere-presentazione/software-ats-cv] |
| LinkedIn | Live | The four most recently uploaded resumes are retained for reuse [https://www.linkedin.com/help/linkedin/answer/a512405]; a saved resume is not automatically sent with every application [https://www.linkedin.com/help/linkedin/answer/a506429] |
| InfoJobs Italia | Closed | Activity ended 31 December 2025; user data are deleted definitively at closure [https://assistenza.infojobs.it/hc/it/articles/23116648861084-CHIUSURA-INFOJOBS-ITALIA] |
| InfoCamere | Not a channel | Registry lookup to check that an employer exists and its size only |

## 4. Portal CV versus public competition CV

- **Portal CV.** Built field by field inside the platform and the artefact actually applied with; there is no general "upload my own PDF instead" route [https://www.inpa.gov.it/faq-domande-e-risposte/].
- **Competition CV.** Each bando is the authority. Bandi require the stated requirements to be declared under Articles 46 and 47 of D.P.R. 445/2000 [https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=432f5b444aee41f1b30791043d1efac3], and a bando may separately require a signed European-format CV. Whether the inPA portal CV formally constitutes a *dichiarazione sostitutiva* is UNVERIFIED: the inPA FAQ does not use that phrase. Treat it as a self-declaration whose contents are legally enforceable, and confirm signature and attachment rules per bando.
- **Europass.** The format to use when a bando or an EU-facing advert asks for it [https://europass.europa.eu/it/create-europass-cv]. Its ESCO occupation and skill wording is ordinary text, never a printed code or URI [https://europass.europa.eu/en/what-esco-and-how-it-used-europass].

## 5. Hiring incentives

**In force — Bonus ZES 2026, Article 3** [https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A03291&art.dataPubblicazioneGazzetta=2026-06-27&art.flagTipoArticolo=0&art.idArticolo=3&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=0&art.versione=1]: private employers hiring non-managerial permanent staff between 1 January and 31 December 2026 receive a 100% exemption from employer social-security contributions, excluding INAIL premiums, capped at 650 euro per month per worker for up to 24 months. Conditions in the text: at most 10 employees in the month of hire; hire at a site in a ZES unica region; worker aged 35 or over and unemployed at least 24 months; net employment increase; no domestic work or apprenticeship; no individual or collective dismissals in the preceding six months; 26 million euro budget for 2026; not cumulable with other exemptions; granted under Regulation (EU) 651/2014.

**Kept uncertain, as found.** Whether a given candidate meets the 24-month unemployment test, how that test is counted, the effect of the 26 million euro cap, the current INPS procedure and the non-cumulability rules are not settled by the article's text. Confirm with the employer's consulente del lavoro or current INPS guidance. Any "clearly fits" conclusion is UNVERIFIED and is not a legal guarantee.

**Resting on an expired basis — over-50 relief, Law 92/2012 art. 4(8)–(11)** [https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2012-06-28;092~art4]: a 50% reduction of employer contributions for 12 months for workers aged 50 or over who have been unemployed for more than 12 months, extended to 18 months on conversion to, or hire as, permanent. The same article applies those paragraphs "nel rispetto del regolamento (CE) n. 800/2008", and that regulation states it applies until 31 December 2013 [https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32008R0800]. Treat the relief as UNVERIFIED and do not count it in a strategy; confirm the current INPS "92-2012" module. Women-only and under-35 incentives are not interchangeable with it.

**Why never on a CV.** The benefit is computed from the employer's contribution position, net employment increase and dismissal history — facts the candidate does not hold and cannot truthfully assert, and eligibility can change before hire. A CV is self-declared, so an incentive claim is either a factual error or an unenforceable promise. Incentives, channel selection, file naming and certificate checks belong in the internal delivery sheet only.

## 6. File size and format limits

| Platform | Formats | Size / count | Status |
|---|---|---|---|
| Indeed | .doc, .docx, .txt, .rtf; PDF auto-converted [https://www.indeed.com/career-advice/resumes-cover-letters/how-to-upload-resume-to-indeed] | One file at a time; upload replaces the previous [https://support.indeed.com/hc/en-ca/articles/11314976176141-FAQs-Creating-Uploading-and-Managing-a-Resume-File] | The widely repeated 5 MB cap is not confirmed on Indeed's own help pages — UNVERIFIED |
| LinkedIn | PDF, DOC and DOCX reported — UNVERIFIED | Four most recent retained [https://www.linkedin.com/help/linkedin/answer/a512405] | The 2 MB figure is third-party and conflicts with a reported 5 MB elsewhere; LinkedIn's pages checked publish no limit — UNVERIFIED |
| inPA | CV compiled in the portal; PDF downloadable [https://www.inpa.gov.it/faq-domande-e-risposte/] | UNVERIFIED | Per-bando attachment rules prevail |
| ClicLavoro Basilicata | CV published in the portal; SPID [https://lavoro.regione.basilicata.it/servizio/cliclavoro-basilicata/] | UNVERIFIED | — |
| EURES / Europass | Structured Europass fields linked to EURES [https://eures.europa.eu/looking-work-europe-heres-how-changes-eures-portal-affect-you-2025-03-18_it] | UNVERIFIED | — |

Where an advert names its own parser, file name, file type or size, the advert overrides these defaults.

## 7. Consolidated open questions

- Italian section order and exact headings: convention, not sourced. UNVERIFIED.
- Whether a portal CV is formally a *dichiarazione sostitutiva*: confirm per bando. UNVERIFIED.
- Indeed and LinkedIn upload size limits: not published on the vendor pages checked. UNVERIFIED.
- ZES qualification for a given candidate, the unemployment-duration counting method and the current INPS procedure. UNVERIFIED.
- Over-50 relief in Law 92/2012 art. 4(8)–(11): its cited basis, Regulation (EC) 800/2008, applied only until 31 December 2013. UNVERIFIED.
- Two-page maximum: convention, not a rule. UNVERIFIED.
- EURES "explicit consent" wording: not stated on the support page checked. UNVERIFIED.
