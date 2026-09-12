# -*- coding: utf-8 -*-
"""The guide and cover parts of a dossier.

These two parts are not sent to an employer: they tell the candidate which file to
send where, how to print it, and what to check before pressing send. They are part
of the package because the most common failure is not a badly written CV, it is the
right CV sent in the wrong format to the wrong channel.

Defaults are in Italian and English; pass your own lists to override them, because
channels change and a package cannot track every job board.
"""
from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

from .docx_kit import (
    cell_shade, fixed_layout, header_row, body_row, keep_rows_together, page_break,
    para, para_border, para_shade, table_widths,
)
from .model import CV
from .theme import Preset
from .variants import _section, make_styles

# ---------------------------------------------------------------------------
# Channel matrix: where to send which file, and what the channel does with it
# ---------------------------------------------------------------------------
CHANNELS = {
    "it": [
        ("Portali italiani (per esempio Indeed, LinkedIn)",
         "CV ATS, lingua italiana",
         "Il .docx è letto meglio del PDF dai sistemi di selezione; il PDF resta "
         "accettato. Nessuna tabella, nessuna icona, nessuna foto."),
        ("Portale regionale e Centro per l'Impiego",
         "CV ATS + versione da consegna a mano",
         "Serve l'identità digitale (SPID o CIE) per pubblicare il curriculum e "
         "candidarsi agli avvisi. Allo sportello il cartaceo aiuta."),
        ("Concorsi e selezioni pubbliche",
         "CV ATS",
         "Il curriculum compilato nel portale fa fede e vale come dichiarazione "
         "sostitutiva: il bando prevale su qualsiasi formato. Allegare il PDF solo "
         "se il bando lo ammette."),
        ("EURES / Europass",
         "CV in inglese",
         "Le candidature EURES passano da un profilo Europass: va creato, compilato "
         "nei campi strutturati e condiviso con consenso esplicito. Il PDF da solo "
         "non basta."),
        ("Aziende estere",
         "CV in inglese",
         "PDF con testo selezionabile. Se l'annuncio chiede una lettera, usare la "
         "versione nella lingua dell'annuncio."),
        ("Consegna a mano, segnalazioni, agenzie",
         "Versione curata con foto",
         "Stampata a colori. È la versione con i dati anagrafici e la firma, per chi "
         "se li aspetta ancora."),
        ("Candidatura spontanea per e-mail",
         "CV ATS o curato + lettera",
         "Oggetto esplicito: ruolo, nome, città. Testo breve, curriculum in allegato."),
    ],
    "en": [
        ("Job boards",
         "ATS CV in the language of the advert",
         "Send .docx when the platform prefers it, PDF otherwise. No table, no icon, "
         "no photo."),
        ("Public employment service",
         "ATS CV + designed CV",
         "Most services require a digital identity to publish the profile. Take the "
         "printed version to the counter."),
        ("Cross-border applications (EURES/Europass)",
         "ATS CV in English",
         "EURES applications go through a Europass profile with structured fields and "
         "explicit sharing consent."),
        ("Direct employer or agency",
         "Designed CV",
         "Printed in colour. This is the version that may carry personal details and "
         "a signature."),
        ("Speculative application by e-mail",
         "ATS CV or designed CV + cover letter",
         "State the role, the name and the city in the subject line."),
    ],
}

PRINT_RULES = {
    "it": [
        "Formato A4 verticale (210 x 297 mm). Non usare il formato Letter.",
        "Scala di stampa 100%, dimensione reale: mai “adatta alla pagina”.",
        "Fronte/retro attivo con rilegatura sul lato corto: due pagine, un foglio.",
        "Prova in scala di grigi prima di stampare: nessun testo deve sbiadire.",
        "Tenere il contenuto ad almeno 10 mm dal bordo del foglio.",
        "Carta bianca da 80-100 g/m²; evitare la carta lucida, si vede male in "
        "scansione.",
        "Firmare con penna nera sopra la firma stampata nella versione da consegnare.",
        "Conservare il PDF, non solo il .docx: il PDF è ciò che il destinatario vede.",
    ],
    "en": [
        "A4 portrait (210 x 297 mm). Never US Letter for a European recipient.",
        "Print at 100%, actual size. Never “fit to page”.",
        "Duplex with short-edge binding: two pages, one sheet.",
        "Check a greyscale print: no text may fade into the background.",
        "Keep all content at least 10 mm inside the paper edge.",
        "80-100 g/m² white paper. Avoid glossy stock: it scans badly.",
        "Sign in black ink above the printed signature on the hand-delivery version.",
        "Keep the PDF, not only the .docx: the PDF is what the reader sees.",
    ],
}

CHECKLIST = {
    "it": [
        "Telefono ed e-mail corretti, cellulare attivo, indirizzo e-mail professionale.",
        "Il PDF ha un vero livello di testo: prova a copiare una riga, se non si copia "
        "il curriculum è un'immagine.",
        "Il nome del file segue lo schema concordato, senza spazi né date “final”.",
        "I dati coincidono con il documento ufficiale che un datore di lavoro può "
        "chiedere (per esempio l'estratto contributivo).",
        "Nessuna dichiarazione di validità di attestati o abilitazioni non verificata "
        "sul documento originale.",
        "Le date sono tutte nello stesso formato.",
        "Nessun errore di ortografia nel nome dell'azienda a cui ti rivolgi.",
        "Prima di fornire referenze, il referente è stato avvisato e ha acconsentito.",
    ],
    "en": [
        "Phone and e-mail correct, mobile switched on, professional address.",
        "The PDF has a real text layer: copy one line, if it does not copy the CV is "
        "an image.",
        "The file name follows the agreed scheme: no spaces, no “final”, no version "
        "numbers.",
        "The facts match the official record an employer can request.",
        "No claim of validity for a certificate you have not checked.",
        "Every date uses the same format.",
        "No spelling mistakes in the name of the company you are writing to.",
        "References have been asked and agreed before being offered.",
    ],
}

FILE_NAMES = {
    "it": [
        ("<Cognome>_CV_ATS_<LINGUA>.docx", "Curriculum per i portali, nella lingua "
         "dell'annuncio."),
        ("<Cognome>_CV_ATS_<LINGUA>.pdf", "Stessa versione in PDF, quando il portale "
         "accetta solo PDF."),
        ("<Cognome>_CV_CURATO.pdf", "Versione da stampa e da consegna a mano."),
        ("<Cognome>_CV_MASTER.docx", "Documento unico da modificare: tutte le parti."),
        ("<Cognome>_CV_ATS_<LINGUA>.txt", "Solo testo, per i moduli che chiedono di "
         "incollare il curriculum."),
    ],
    "en": [
        ("<Surname>_CV_ATS_<LANG>.docx", "Portal CV, in the language of the advert."),
        ("<Surname>_CV_ATS_<LANG>.pdf", "The same file as PDF, when only PDF is accepted."),
        ("<Surname>_CV_DESIGNED.pdf", "Print and hand-delivery version."),
        ("<Surname>_CV_MASTER.docx", "The single editable file: every part."),
        ("<Surname>_CV_ATS_<LANG>.txt", "Plain text, for forms that ask you to paste."),
    ],
}


def build_guide(doc, cv: CV, p: Preset, channels=None, print_rules=None, checklist=None,
                file_names=None):
    styles = make_styles(doc, p)
    lang = cv.lang if cv.lang in CHANNELS else "it"
    channels = channels or CHANNELS[lang]
    print_rules = print_rules or PRINT_RULES[lang]
    checklist = checklist or CHECKLIST[lang]
    file_names = file_names or FILE_NAMES[lang]
    width = p.page.usable_width_mm

    title = "Guida a invio, esportazione e stampa" if lang == "it" else \
        "Sending, exporting and printing"
    para(doc, title, style=styles["title"])
    para(doc, "Questa parte è per te: non va inviata a nessuno." if lang == "it"
         else "This part is for you: never send it to anyone.",
         style=styles["subhead"])

    _section(doc, styles, p, "1. Quale versione usare per ogni canale" if lang == "it"
             else "1. Which file to send where")
    widths = (58.0, 42.0, width - 100.0)
    table = doc.add_table(rows=1, cols=3)
    table.autofit = False
    fixed_layout(table)
    heading = ("Canale", "Versione", "Come") if lang == "it" else \
        ("Channel", "Which file", "How")
    header_row(table.rows[0].cells, widths, heading, p.palette.primary)
    for index, values in enumerate(channels):
        row = table.add_row()
        body_row(row.cells, widths, values, fill=p.palette.subtle if index % 2 else None)
    keep_rows_together(table)

    _section(doc, styles, p, "2. Impostazioni di stampa" if lang == "it"
             else "2. Print settings")
    para(doc, "Le versioni per i portali usano un carattere neutro e solo nero e "
              "grigio, così restano leggibili dai sistemi automatici e in bianco e "
              "nero. La versione curata usa un serif per i titoli: è pensata per la "
              "carta." if lang == "it" else
              "Portal variants use a neutral typeface in black and grey only: they "
              "stay readable to parsers and in monochrome printing. The designed "
              "variant uses a serif for headings because it is meant for paper.",
         style=styles["body"])
    for rule in print_rules:
        para(doc, "\u2022  " + rule, style=styles["bullet"])

    _section(doc, styles, p, "3. Nomi dei file" if lang == "it" else "3. File names")
    for name, description in file_names:
        para(doc, f"{name} \u2014 {description}", style=styles["bullet"])

    _section(doc, styles, p, "4. Controllo prima dell'invio" if lang == "it"
             else "4. Checklist before sending")
    for item in checklist:
        para(doc, "\u2022  " + item, style=styles["bullet"])

    _section(doc, styles, p, "5. Errori da evitare" if lang == "it"
             else "5. Mistakes to avoid")
    mistakes = ([
        "Modificare il PDF invece del documento sorgente: la correzione va fatta nei "
        "dati e poi riesportata.",
        "Inviare il fascicolo completo a un'azienda: si invia solo la versione del "
        "canale.",
        "Dichiarare un titolo di studio o una qualifica che non si possiede.",
        "Dichiarare valido un attestato scaduto.",
    ] if lang == "it" else [
        "Editing the PDF instead of the source data: fix the data and rebuild.",
        "Sending the whole dossier to an employer: send the channel's file only.",
        "Claiming a qualification you do not hold.",
        "Presenting an expired certificate as current.",
    ])
    for item in mistakes:
        para(doc, "\u2022  " + item, style=styles["bullet"])

    _section(doc, styles, p, "6. Come rigenerare i documenti" if lang == "it"
             else "6. How to rebuild")
    paragraph = para(doc, "cvkit build . -o out   →   cvkit qa out", style=styles["body"])
    para_shade(paragraph, p.palette.light)
    paragraph.paragraph_format.left_indent = Mm(4)
    para(doc, "I contenuti vivono nel file di dati, non nel documento: si corregge il "
              "dato, si rigenera, e tutte le versioni restano allineate." if lang == "it"
         else "Content lives in the data file, not in the document: fix the data, "
              "rebuild, and every variant stays consistent.",
         style=styles["body"])


def build_cover(doc, cv: CV, p: Preset, index_rows, include_notes: bool = True):
    """The front page of a dossier: what the parts are and where each one goes."""
    styles = make_styles(doc, p)
    width = p.page.usable_width_mm
    contact = cv.contact

    para(doc, "FASCICOLO CURRICULUM VITAE", style=styles["small"],
         align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, contact.name, style=styles["name"], align=WD_ALIGN_PARAGRAPH.CENTER)
    if contact.headline:
        para(doc, contact.headline, style=styles["headline"],
             align=WD_ALIGN_PARAGRAPH.CENTER)
    line = " · ".join(x for x in (contact.address or contact.location, contact.phone,
                                  contact.email) if x)
    paragraph = para(doc, line, style=styles["contact"],
                     align=WD_ALIGN_PARAGRAPH.CENTER, after=8)
    para_border(paragraph, "bottom", p.palette.rule, 6, 6)

    _section(doc, styles, p, "Come è organizzato questo fascicolo")
    para(doc, "Un unico documento con tutte le versioni richieste dai diversi canali. "
              "Ogni parte inizia su una pagina nuova, quindi si può usare da sola "
              "senza perdere l'impaginazione.", style=styles["body"])

    rows = [r for r in index_rows if include_notes or not str(r[0]).lower().startswith(
        ("ultima", "last"))]
    widths = (26.0, 62.0, width - 88.0)
    table = doc.add_table(rows=1, cols=3)
    table.autofit = False
    fixed_layout(table)
    header_row(table.rows[0].cells, widths, ("Parte", "Contenuto", "Dove e come usarla"),
               p.palette.primary)
    for index, values in enumerate(rows):
        row = table.add_row()
        body_row(row.cells, widths, values, size=9,
                 fill=p.palette.subtle if index % 2 else None)
    keep_rows_together(table)

    paragraph = para(doc, "Nota: le versioni per i portali non contengono data di "
                          "nascita, stato civile, numero di figli né foto. La versione "
                          "da consegna a mano li riporta, perché in quel contesto sono "
                          "ancora attesi.", style=styles["small"], before=8)
    para_border(paragraph, "top", p.palette.rule, 6, 4)
