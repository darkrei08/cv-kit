"""A synthetic CV used by the test suite and by continuous integration.

Every fact here is invented. The repository is public, so no real person, employer
or address appears anywhere in it — and the test data must not become an exception
to that rule. The shape of the data mirrors a real long-career profile: several
fixed-term contracts, one long permanent job, licences, safety training.
"""
from cvkit import CV, Contact, Education, Job, Language, Letter, SkillGroup

cv = CV(
    contact=Contact(
        name="Giulia Bianchi",
        headline="Tecnica di manutenzione elettrica",
        subheadline="Quadri di automazione · Ricerca guasti · Conduzione impianti",
        email="giulia.bianchi@example.com",
        phone="+39 000 000 0000",
        location="Bologna (BO), Italia",
        address="Via Esempio 1 – 40100 Bologna (BO), Italia",
        personal={
            "Data e luogo di nascita": "01/01/1975 – Bologna (BO)",
            "Stato civile": "Coniugata, due figli",
            "Codice fiscale": "XXXXXX00X00X000X",
        },
        place_date="Bologna, settembre 2026",
    ),
    profile=(
        "Tecnica di manutenzione elettrica con esperienza continuativa dal 2001 su "
        "quadri di automazione e impianti di processo. Dodici anni consecutivi nella "
        "stessa azienda manifatturiera, con passaggio da manutentrice a responsabile "
        "di linea. Abituata a turni, a interventi in fermo impianto e alla gestione "
        "autonoma dei guasti su PLC e inverter. Disponibile a trasferte."
    ),
    experience=[
        Job(
            period="03/2013 – 06/2025",
            employer="Industrie Esempio S.p.A.",
            location="Bologna (BO)",
            sector="Manifattura – imballaggi",
            role="Manutentrice elettrica e responsabile di linea",
            contract="Tempo indeterminato, full time. Cessato per riduzione del "
                     "personale.",
            duties=[
                "Manutenzione preventiva e correttiva su quadri di automazione, "
                "inverter e motori.",
                "Ricerca guasti su impianti controllati da PLC e riduzione dei fermi "
                "macchina.",
                "Coordinamento di due tecnici sulla linea di confezionamento.",
            ],
        ),
        Job(
            period="09/2005 – 02/2013",
            employer="Impianti Esempio S.r.l.",
            location="Modena (MO)",
            sector="Installazione e manutenzione impianti",
            role="Elettricista installatrice",
            contract="Tempo determinato, full time, contratti rinnovati più volte.",
            duties=[
                "Installazione e collaudo di quadri elettrici presso clienti "
                "industriali.",
                "Lettura di schemi elettrici e posa di canalizzazioni e cablaggi.",
            ],
        ),
        Job(
            period="01/2001 – 08/2005",
            employer="Prime esperienze – Bologna e provincia",
            location="Bologna (BO)",
            sector="Elettrotecnica e installazione",
            role="Apprendista elettricista e aiuto installatore",
            contract="Tempo determinato e apprendistato.",
            duties=[
                "Aiuto installatore su impianti civili e industriali.",
                "Preparazione di quadri, cablaggi e collaudi con il responsabile.",
            ],
        ),
    ],
    education=[
        Education(
            year="2019",
            title="Aggiornamento per addetti al primo soccorso aziendale",
            where="Ente accreditato – attestato conseguito",
        ),
        Education(
            year="2019",
            title="Formazione per addetti alla prevenzione incendi",
            where="Ente accreditato – attestato conseguito",
        ),
        Education(
            year="1998",
            title="Diploma di istituto tecnico industriale, indirizzo elettrotecnico",
            where="ITIS – Bologna",
        ),
    ],
    skills=[
        SkillGroup(
            label="Manutenzione elettrica",
            text="Quadri di automazione, inverter, motori, ricerca guasti, lettura di "
                 "schemi elettrici, strumenti di misura.",
        ),
        SkillGroup(
            label="Controllo di processo",
            text="Programmazione di base di PLC, supervisione di linea, gestione "
                 "allarmi e registri di manutenzione.",
        ),
        SkillGroup(
            label="Sicurezza e organizzazione",
            text="Procedure di isolamento, permessi di lavoro, sicurezza in fermo "
                 "impianto, coordinamento di piccole squadre.",
        ),
    ],
    personal_skills=[
        "Autonomia tecnica: interviene su un guasto e documenta l'intervento.",
        "Continuità: dodici anni consecutivi nella stessa azienda.",
        "Collaborazione con produzione e manutenzione meccanica su turni.",
    ],
    licences=[
        "Patente di guida B.",
        "Abilitazione PES/PAV per lavori elettrici.",
        "Attestati di primo soccorso e antincendio (2019).",
    ],
    licence_note="Gli attestati vanno verificati con l'ente che li ha rilasciati prima "
                 "di dichiararne la validità.",
    languages=[
        Language(name="Italiano", level="Madrelingua"),
        Language(name="Inglese", level="Livello B1 – lettura di manuali tecnici"),
    ],
    availability=[
        "Disponibile full-time, su turni, anche notturni e nei fine settimana.",
        "Disponibile a trasferte e a interventi programmati in fermo impianto.",
    ],
    keywords="quadri di automazione, inverter, PLC, motori elettrici, ricerca guasti, "
             "schemi elettrici, strumenti di misura, manutenzione preventiva, "
             "isolamento e permessi di lavoro, coordinamento squadre",
    motivation=[
        ("1. Manutenzione che riduce i fermi macchina",
         "Dodici anni sulla stessa linea di confezionamento: gli interventi "
         "ricorrenti, le cause dei fermi e le soluzioni sono già noti, senza "
         "formazione iniziale."),
        ("2. Continuità dimostrabile",
         "Dodici anni consecutivi nella stessa azienda, con passaggio da manutentrice "
         "a responsabile di linea: dati verificabili, non autodichiarati."),
        ("3. Operativa dal primo giorno",
         "Abilitazione per lavori elettrici già posseduta, esperienza su turni e in "
         "fermo impianto, disponibilità a trasferte."),
    ],
    sectors=[
        ("Manutenzione elettrica industriale",
         "Quadri, inverter, motori, ricerca guasti, PLC.",
         "Manutentrice elettrica, tecnica di impianti, addetta al collaudo."),
        ("Installazione e collaudo impianti",
         "Quadri elettrici presso clienti industriali, cablaggi, collaudi.",
         "Installatrice elettrica, tecnica di cantiere, collaudatrice."),
        ("Conduzione e supervisione di linea",
         "Responsabile di linea, coordinamento di due tecnici, registri di "
         "manutenzione.",
         "Capoturno, responsabile di linea, coordinatrice di manutenzione."),
    ],
    letter=Letter(
        subject="Candidatura spontanea – tecnica di manutenzione elettrica",
        paragraphs=[
            "Gentile Responsabile, mi chiamo Giulia Bianchi e propongo la mia "
            "candidatura per una posizione di manutenzione elettrica industriale.",
            "Ho esperienza continuativa dal 2001, con dodici anni consecutivi nella "
            "stessa azienda manifatturiera come manutentrice elettrica e responsabile "
            "di linea: manutenzione su quadri di automazione, inverter e motori, "
            "ricerca guasti su impianti controllati da PLC e coordinamento di due "
            "tecnici sulla linea di confezionamento.",
            "Ho l'abilitazione per lavori elettrici e gli attestati di primo soccorso "
            "e antincendio conseguiti nel 2019. Sono disponibile a turni, anche "
            "notturni, e a trasferte per interventi in fermo impianto.",
            "Resto a disposizione per un colloquio tecnico o per una prova pratica.",
        ],
        closing="Ringrazio per l'attenzione e porgo distinti saluti.",
        variants=[
            ("Variante A – manutenzione elettrica industriale",
             ["Dodici anni sulla stessa linea di confezionamento.",
              "Riduzione dei fermi macchina tramite manutenzione preventiva.",
              "Disponibile a prova pratica su quadri di automazione."]),
            ("Variante B – installazione e collaudo",
             ["Sei anni di installazione di quadri elettrici presso clienti "
              "industriali.",
              "Lettura di schemi, cablaggi, collaudo e messa in servizio."]),
        ],
    ),
    verification_notes=[
        ("Validità degli attestati",
         "Confermare con l'ente che ha rilasciato gli attestati del 2019 la data di "
         "scadenza e l'eventuale aggiornamento dovuto prima di dichiararli validi."),
        ("Codice fiscale di esempio",
         "Nel file dimostrativo il codice fiscale è un segnaposto: viene usato solo "
         "per verificare che i controlli automatici lo escludano dalle versioni per "
         "i portali."),
    ],
)

#: Italian label overrides are unnecessary: the defaults in cvkit.model.LABELS["it"]
#: already match. Kept as a comment so a reader knows the knob exists.

#: The timeline drawn on the motivation page.
timeline = [
    ("2001", "Inizio attività come apprendista elettricista"),
    ("2005", "Elettricista installatrice su impianti industriali (9 anni)"),
    ("2013", "Manutentrice elettrica e responsabile di linea (12 anni)"),
    ("2019", "Attestati di primo soccorso e antincendio"),
    ("2025", "Conclusione del rapporto per riduzione del personale"),
]
