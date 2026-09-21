"""Visual presets.

Two presets matter:

* ``ats`` — the document that a parser reads. One column, one neutral sans-serif
  family, black text on white, grey rules, no colour, no image, no table. Colour is
  not what breaks a parser; tables, text boxes and images are. Colour is removed
  anyway because the same file is often printed in black and white, and because a
  keyword does not become more true when it is blue.
* ``designed`` — the document that a person reads on paper. A serif for headings,
  a modest accent, rules and a two-column tail. Never sent to a parser.

Both presets are numbers, not opinions: changing a value here changes every
document the package produces.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    ink: str = "000000"          # body text
    muted: str = "333333"        # secondary text: dates, places, contract type
    primary: str = "000000"      # headings and the rules under them
    accent: str = "000000"       # emphasis inside a line
    rule: str = "8C8C8C"         # separator colour
    light: str = "F2F4F6"        # shaded block background
    subtle: str = "FAFBFC"       # alternating table row
    marker: str = "404040"       # bullet glyph
    body_font: str = "Arial"
    head_font: str = "Arial"


#: The ATS palette: black, white and grey only.
ATS = Palette()

#: The designed palette: a restrained navy and teal, serif headings.
DESIGNED = Palette(
    ink="1F2933",
    muted="5B6770",
    primary="14395F",
    accent="0F6E6E",
    rule="C7D3DE",
    light="EEF3F7",
    subtle="F7F9FB",
    marker="0F6E6E",
    body_font="Calibri",
    head_font="Georgia",
)

PALETTES: dict[str, Palette] = {"ats": ATS, "designed": DESIGNED}


@dataclass(frozen=True)
class PageSpec:
    """A4 margins in millimetres."""

    top: float = 14.0
    right: float = 16.0
    bottom: float = 14.0
    left: float = 16.0
    width_mm: float = 210.0
    height_mm: float = 297.0

    @property
    def usable_width_mm(self) -> float:
        return self.width_mm - self.left - self.right

    @property
    def usable_height_mm(self) -> float:
        return self.height_mm - self.top - self.bottom


#: Tight enough to hold a long career in two pages without shrinking the body text
#: below 9.5 pt. Documented as a deliberate deviation in docs/knowledge.
ATS_PAGE = PageSpec(top=14, right=16, bottom=14, left=16)

#: Slightly airier, for documents that are read on paper.
DESIGNED_PAGE = PageSpec(top=15, right=17, bottom=15, left=17)

PAGES: dict[str, PageSpec] = {"ats": ATS_PAGE, "designed": DESIGNED_PAGE}


@dataclass(frozen=True)
class TypeScale:
    """Point sizes for every role, so nothing is hard-coded in a builder."""

    name: float = 19.0
    headline: float = 11.0
    subheadline: float = 9.5
    contact: float = 9.5
    section: float = 10.0
    employer: float = 10.0
    role: float = 10.0
    meta: float = 9.0
    body: float = 10.0
    bullet: float = 9.5
    small: float = 8.5
    line_spacing: float = 1.06
    body_spacing: float = 1.10
    section_before: float = 4.0
    section_after: float = 2.0
    entry_before: float = 3.0
    bullet_after: float = 0.4


#: Tuned to fit a dense, long career in two A4 pages at 9.5-10 pt.
ATS_TYPE = TypeScale()

#: The designed variant can afford slightly larger secondary text.
DESIGNED_TYPE = TypeScale(
    section=10.5,
    meta=8.5,
    bullet=9.2,
    body=9.2,
    line_spacing=1.06,
    body_spacing=1.08,
    section_before=6.0,
    section_after=3.0,
    entry_before=3.0,
    bullet_after=0.2,
)

TYPES: dict[str, TypeScale] = {"ats": ATS_TYPE, "designed": DESIGNED_TYPE}


@dataclass(frozen=True)
class Preset:
    name: str
    palette: Palette
    page: PageSpec
    type: TypeScale
    single_column: bool
    allow_tables: bool
    allow_images: bool


def preset(name: str) -> Preset:
    key = name if name in PALETTES else "ats"
    return Preset(
        name=key,
        palette=PALETTES[key],
        page=PAGES[key],
        type=TYPES[key],
        single_column=key == "ats",
        allow_tables=key == "designed",
        allow_images=key == "designed",
    )
