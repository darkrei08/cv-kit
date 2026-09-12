# -*- coding: utf-8 -*-
"""Data model for a CV.

The whole point of this package is that a CV is data, not a document. Everything a
renderer needs lives in these dataclasses, so the same facts can produce an
ATS-plain file, a designed file, an English file and a cover letter without any of
them drifting from the others.

Fields marked "personal" (birth date, marital status, identity numbers) are *only*
rendered by the designed variant and are flagged by :func:`validate` when a
portal-facing variant is asked for, because they are both unnecessary and a known
discrimination risk.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Section labels
# ---------------------------------------------------------------------------
LABELS: dict[str, dict[str, str]] = {
    "it": {
        "profile": "Profilo professionale",
        "experience": "Esperienza professionale",
        "education": "Istruzione e formazione",
        "skills": "Competenze tecniche",
        "personal_skills": "Competenze trasversali",
        "licences": "Patenti e abilitazioni",
        "languages": "Lingue",
        "availability": "Disponibilità",
        "sectors": "Posizioni compatibili",
        "keywords": "Attrezzature e macchine",
        "personal": "Dati personali",
        "period": "Periodo:",
        "declaration": "Dichiaro che le informazioni riportate nel presente curriculum "
                       "vitae sono veritiere.",
        "signature": "In fede",
        "gdpr": "Autorizzo il trattamento dei miei dati personali ai sensi del "
                "Regolamento (UE) 2016/679 (GDPR) e del D.Lgs. 196/2003.",
        "motivation_title": "Perché questo profilo",
        "letters_title": "Lettere di presentazione",
        "appendix_title": "Allegato operativo",
    },
    "en": {
        "profile": "Professional profile",
        "experience": "Work experience",
        "education": "Education and training",
        "skills": "Technical skills",
        "personal_skills": "Personal skills",
        "licences": "Driving licences and qualifications",
        "languages": "Languages",
        "availability": "Availability",
        "sectors": "Suitable positions",
        "keywords": "Machines and equipment",
        "personal": "Personal details",
        "period": "Period:",
        "declaration": "I declare that the information in this curriculum vitae is truthful.",
        "signature": "Signed",
        "gdpr": "I authorise the processing of my personal data in accordance with "
                "Regulation (EU) 2016/679 (GDPR) and Italian Legislative Decree 196/2003.",
        "motivation_title": "Why this profile",
        "letters_title": "Cover letters",
        "appendix_title": "Supporting appendix",
    },
}


@dataclass
class Contact:
    """Identity and reachability. Keep the short location for portal variants."""

    name: str
    headline: str = ""
    subheadline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""            # short form, e.g. "Bologna (BO), Italia"
    address: str = ""             # full street address — designed variant only
    personal: dict[str, str] = field(default_factory=dict)
    # personal is free-form so a country's own conventions can be expressed, e.g.
    # {"Data e luogo di nascita": "...", "Stato civile": "...", "Codice fiscale": "..."}
    photo: str = ""               # path; designed variant only
    signature: str = ""           # path; designed variant only
    place_date: str = ""          # e.g. "Bologna, settembre 2026"


@dataclass
class Job:
    period: str
    employer: str
    role: str
    sector: str = ""
    location: str = ""
    contract: str = ""
    duties: list[str] = field(default_factory=list)

    def meta(self, separator: str = " · ") -> str:
        """Everything factual about the job except the dates, in one line."""
        return separator.join(x for x in (self.location, self.sector, self.contract) if x)


@dataclass
class Education:
    title: str
    year: str = ""
    where: str = ""


@dataclass
class SkillGroup:
    label: str
    text: str


@dataclass
class Language:
    name: str
    level: str


@dataclass
class Letter:
    """A cover letter, in one or more variants of the middle paragraphs."""

    subject: str = ""
    greeting: str = "Gentile Responsabile,"
    paragraphs: list[str] = field(default_factory=list)
    closing: str = ""
    variants: list[tuple[str, list[str]]] = field(default_factory=list)


@dataclass
class CV:
    contact: Contact
    profile: str = ""
    experience: list[Job] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    skills: list[SkillGroup] = field(default_factory=list)
    personal_skills: list[str] = field(default_factory=list)
    licences: list[str] = field(default_factory=list)
    licence_note: str = ""
    languages: list[Language] = field(default_factory=list)
    availability: list[str] = field(default_factory=list)
    keywords: str = ""
    motivation: list[tuple[str, str]] = field(default_factory=list)
    sectors: list[tuple[str, str]] = field(default_factory=list)
    letter: Letter | None = None
    lang: str = "it"
    #: The portal variants omit the year of a school qualification: it is an age
    #: cue with no selection value. Set to False to keep it.
    hide_education_years_in_ats: bool = True
    labels: dict[str, str] = field(default_factory=dict)
    # Text inserted verbatim, e.g. the privacy notice required by a country.
    privacy_notice: str = ""
    # Internal notes are never rendered by the portal-facing variants.
    verification_notes: list[tuple[str, str]] = field(default_factory=list)

    def label(self, key: str) -> str:
        if key in self.labels:
            return self.labels[key]
        return LABELS.get(self.lang, LABELS["it"]).get(key, key)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
GENERIC_PHRASES = (
    # Phrases that carry no verifiable information. They are the first thing a
    # recruiter discards, and some of them are age cues.
    "hard worker", "hard-working", "dynamic", "young at heart", "excellent it skills",
    "team player with excellent", "ottime capacità relazionali",
)
AGE_CUES = ("40 anni", "40 years", "30 anni", "30 years", "oltre 40", "over 40")

# Fields that must not appear in a portal-facing document.
PERSONAL_FORBIDDEN_IN_ATS = (
    "birth", "nascita", "marital", "coniug", "figli", "children", "codice fiscale",
    "fiscal", "nazionalita", "nationality", "photo", "foto", "age", "eta",
)


@dataclass
class Finding:
    level: str      # "error" | "warning" | "info"
    code: str
    message: str
    where: str = ""

    def __str__(self) -> str:
        prefix = {"error": "FAIL", "warning": "WARN", "info": "INFO"}.get(self.level, "?")
        place = f" [{self.where}]" if self.where else ""
        return f"{prefix} {self.code}{place}: {self.message}"


def validate(cv: CV, variant: str = "ats") -> list[Finding]:
    """Check a CV against the rules that keep it usable and honest.

    `variant` matters: the designed variant is allowed personal data and a photo,
    the portal-facing variants are not.
    """
    out: list[Finding] = []

    if not cv.contact.name.strip():
        out.append(Finding("error", "missing-name", "the name is empty"))
    if not cv.contact.email.strip():
        out.append(Finding("error", "missing-email", "no email address"))
    elif "@" not in cv.contact.email:
        out.append(Finding("error", "bad-email", f"'{cv.contact.email}' is not an address"))
    if not cv.contact.phone.strip():
        out.append(Finding("warning", "missing-phone", "no phone number"))
    if not cv.contact.headline.strip():
        out.append(Finding("warning", "missing-headline",
                           "no headline: portals match the headline against the advert"))

    if not cv.experience:
        out.append(Finding("error", "no-experience", "an empty work history"))
    for i, job in enumerate(cv.experience):
        where = f"experience[{i}]"
        if not job.period.strip():
            out.append(Finding("error", "job-without-dates",
                               f"'{job.employer}' has no date range", where))
        if not job.role.strip():
            out.append(Finding("error", "job-without-role",
                               f"'{job.employer}' has no role", where))
        if len(job.duties) > 5:
            out.append(Finding("warning", "too-many-duties",
                               f"{len(job.duties)} bullets; four is the practical maximum",
                               where))

    if not cv.profile.strip():
        out.append(Finding("warning", "missing-profile",
                           "no profile paragraph: the first screen of a CV is the "
                           "most read part"))
    profile_words = len(cv.profile.split())
    if profile_words > 130:
        out.append(Finding("warning", "profile-too-long",
                           f"profile is {profile_words} words; keep it under 130 "
                           f"(four lines)"))

    text_blocks = [cv.profile] + [d for j in cv.experience for d in j.duties]
    joined = " ".join(text_blocks).lower()
    for phrase in GENERIC_PHRASES:
        if phrase in joined:
            out.append(Finding("warning", "generic-phrase",
                               f"'{phrase}' carries no verifiable information"))
    for cue in AGE_CUES:
        if cue in joined:
            out.append(Finding("warning", "age-cue",
                               f"'{cue}' signals age; substitute the verifiable "
                               f"periods (for example '17 years with one employer')"))

    if variant in {"ats", "ats_en", "portal"}:
        blob = " ".join(
            [cv.contact.address, *cv.contact.personal.keys(), *cv.contact.personal.values()]
        ).lower()
        for token in PERSONAL_FORBIDDEN_IN_ATS:
            if token in blob:
                out.append(Finding(
                    "warning", "personal-data-in-portal-variant",
                    f"the portal variant would carry '{token}'; keep personal data in "
                    f"the designed variant only"))
        if cv.contact.photo:
            out.append(Finding("warning", "photo-in-portal-variant",
                               "a photo breaks parsing and invites discrimination; "
                               "keep it in the designed variant"))
        if not cv.keywords.strip():
            out.append(Finding("warning", "no-keywords",
                               "no keyword line: automatic screening matches on terms "
                               "that appear as ordinary text"))
        else:
            count = len([k for k in cv.keywords.split(",") if k.strip()])
            if count < 10:
                out.append(Finding("info", "few-keywords",
                                   f"{count} keywords; 10 to 14 terms is the useful range"))

    if variant == "designed" and not cv.contact.personal:
        out.append(Finding("info", "no-personal-block",
                           "the designed variant declares no personal details; that is "
                           "correct for some countries and expected in others"))

    for label, path in (("photo", cv.contact.photo), ("signature", cv.contact.signature)):
        if path and not Path(path).exists():
            out.append(Finding(
                "error", "missing-asset",
                f"the {label} '{path}' does not exist: the designed variant would be "
                f"built without it, silently"))

    for i, (title, why) in enumerate(cv.verification_notes):
        if not title.strip() or not why.strip():
            out.append(Finding("warning", "empty-verification-note",
                               "a verification note has an empty title or body",
                               f"verification_notes[{i}]"))
    return out


def errors(findings: Iterable[Finding]) -> list[Finding]:
    return [f for f in findings if f.level == "error"]
