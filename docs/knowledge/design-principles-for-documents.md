# Design principles for a printed document

Design principles for interfaces transfer to a printed CV better than expected, because
both are read in a hurry by someone who did not choose to read them. The principles
below are adapted from two community design skills for coding agents —
[impeccable](https://github.com/pbakaus/impeccable) and
[design-taste](https://github.com/h3nryprod01/design-taste) — which in turn synthesise
the same lineage of "taste is trained, and unseen details compound". Their words are
not reproduced here; what follows is the print translation.

## The anti-generic rules

A document looks machine-generated when the layout is doing decoration instead of
work. On a CV, these are the tells:

| Tell | Why it reads as generic |
|---|---|
| The default template look: centred name, coloured banner, grey sidebar | It is recognisable as something produced without a decision |
| Colour used for decoration rather than emphasis | A second colour should mark one thing, not five |
| Icons standing in for information (a phone glyph before the number, a pin before the city) | They add no information, they break text extraction, and they date instantly |
| Boxes around everything | A border around each section replaces hierarchy with furniture |
| Letter-spaced capitals with no hierarchy behind them | Styling that imitates importance without establishing it |
| A 2 pt difference between two heading levels | It is not a level, it is noise |
| Five type sizes and three families | Each new size dilutes the meaning of the others |
| Justified text in a narrow measure | Rivers of white space, and uneven word spacing |

The single test that catches most of it: **cover the content and look at the shape.**
If the page still looks like a form with boxes filled in, rather than a document with a
reading order, the layout is decorating.

## Hierarchy: one signal per level

A reader's eye needs exactly one unmistakable cue per level, and the same cue every
time. Three levels are enough for a CV:

1. **The name**, once, the largest thing on the page.
2. **The section heading**, always in the same treatment, always separated by the same
   amount of space.
3. **The job entry**: employer in bold, role in a second weight or colour, dates in a
   muted third weight.

Anything beyond three levels needs a reason. When a document has five, none of them
reads as more important than the others, and the reader stops using them.

Whitespace is the strongest tool and the one most often ignored: a section separated by
10 mm of empty space needs no rule, no box and no colour. When space is not available, a
hairline rule is next; a box is last, because it consumes space on four sides to do
what one line does.

## Type

- **One family, plus at most one accent.** A neutral sans-serif for a document that a
  parser reads; a sans-serif body with a serif for headings in the version a person
  reads on paper. A third family needs a reason.
- **A scale with real jumps.** 10 pt for the body, and headings that are clearly
  different — not 10.5. If the eye has to compare two headings to tell them apart, they
  are the same level.
- **Line length matters more than font size** for readability. Around 80 characters per
  line is the target. A 30 mm right margin is one way to reach it; a two-column tail is
  another.
- **Left-aligned, never justified**, in a single-column document.
- Size floors are set by legibility, not by the desire to fit more: 9.5 pt for body
  text is a practical floor for a dense CV, and going below it to save a page is a bad
  trade.

## Colour, and the black-and-white test

Colour is permitted in the version printed and handed to a person; it is pointless in
the version a parser reads. Two constraints apply in both cases:

1. **No information may be carried by colour alone.** If a green heading means
   "verified" and grey means "not", a monochrome print loses the distinction. Use text.
2. **Run the greyscale test.** Navy headings become dark grey and stay legible; a light
   teal becomes a pale grey and disappears. Convert the PDF to greyscale and read it:
   anything that fades is a colour choice that was doing structural work.

Contrast targets for text are the same on paper as on screen: a body text contrast
ratio of 4.5:1 against its background, and 3:1 for large text.

## Two documents, not one compromise

The central architectural decision in this repository: **the same data is rendered
twice** instead of being forced into one document that satisfies neither reader.

The parser wants one column, no table, no image, no text box, and extractable text. The
person wants a page that is pleasant to read, which often means a photo, a second
colour and a two-column tail. Any attempt to satisfy both produces a document that is
weak for each: a table-free but dull portal file, or an attractive file that a parser
mangles.

Rendering twice also settles a subtler problem: the portal version must *not* contain
the personal data that the paper version is expected to contain. Two documents make
that a structural property instead of a discipline.

## Pre-flight checklist

Run this before sending anything. It takes two minutes and catches almost everything.

**Page level**
- [ ] Print or export to PDF at 100%, and look at the actual pages, not the editor.
- [ ] Count the pages: is it inside the limit for this variant?
- [ ] Is anything within 10 mm of the paper edge?
- [ ] Convert to greyscale: does any text fade?

**Section level**
- [ ] Does every section start at the same distance from the previous one?
- [ ] Does every heading use the same treatment?
- [ ] Is there a section whose content is a single short line? Merge it.

**Line level**
- [ ] Is any line of text longer than about 80 characters?
- [ ] Are the dates aligned the same way in every entry?
- [ ] Is any bullet longer than three lines? Split or cut it.

**Fact level**
- [ ] Does every date range agree with the official record?
- [ ] Does every licence and certificate state only what has been verified?
- [ ] Is every claim checkable by the person reading it?

## The principle behind all of it

Every visual choice must survive black-and-white printing at 100% zoom, because that is
how a printed CV is actually seen. A design that only works on a screen, in colour, at
150% zoom is a design that will fail at the moment it matters — which is also why the
automated checks in this repository measure the produced PDF instead of trusting the
source document.
