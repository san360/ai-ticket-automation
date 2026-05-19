"""Default seed data for the ServiceDesk simulator.

This data is used to populate the database on startup and on reset.
It is immutable — always returns a fresh list of ticket dicts.
"""

from attachment_data import (
    VALID_DOCTOR_NOTE_PDF,
    INVALID_RECEIPT_IMAGE,
    VALID_DOCTOR_NOTE_IMAGE,
    MISMATCHED_NAME_CERTIFICATE,
    EXPIRED_CERTIFICATE,
    FICTITIOUS_DOCTOR_CERTIFICATE,
    FAKE_CLINIC_CERTIFICATE,
    VALID_CERTIFICATE_VERIFIABLE,
    GLN_MISMATCH_CERTIFICATE,
)

SEED_TICKETS: list[dict] = [
    {
        "subject": "Krankmeldung ab Montag",
        "description": (
            "Guten Tag, ich bin seit Montag krank und kann nicht zur Arbeit kommen. "
            "Mein Arzt hat mir ein Zeugnis ausgestellt, das ich hier anhänge. "
            "Voraussichtlich bin ich bis Freitag abwesend."
        ),
        "caller_name": "Anna Müller",
        "attachments": [VALID_DOCTOR_NOTE_PDF],
    },
    {
        "subject": "Changement d'adresse",
        "description": (
            "Bonjour, je viens de déménager et j'aimerais mettre à jour mon adresse. "
            "Ma nouvelle adresse est: Rue du Marché 15, 1204 Genève. "
            "Le déménagement a eu lieu le 1er mars."
        ),
        "caller_name": "Pierre Dupont",
    },
    {
        "subject": "Lohnfrage März",
        "description": (
            "Hi, I noticed my March payslip shows a deduction of CHF 450 under "
            "'Other deductions' that I don't understand. Could someone explain what this is for?"
        ),
        "caller_name": "James Wilson",
    },
    {
        "subject": "Mutterschaftsurlaub planen",
        "description": (
            "Liebe HR, ich bin schwanger und möchte meinen Mutterschaftsurlaub planen. "
            "Der errechnete Termin ist am 15. Juli. Ich möchte 2 Wochen vor dem Termin "
            "in den Urlaub gehen. Das ärztliche Attest reiche ich nächste Woche nach."
        ),
        "caller_name": "Sarah Keller",
    },
    {
        "subject": "Signalement comportement inapproprié",
        "description": (
            "Je souhaite signaler un comportement inapproprié de la part d'un collègue. "
            "Depuis plusieurs semaines, cette personne fait des remarques déplacées à mon égard. "
            "Je préfère ne pas donner les détails ici mais j'aimerais en parler à quelqu'un de confiance."
        ),
        "caller_name": "Marie Leclerc",
    },
    {
        "subject": "Cambio dati bancari",
        "description": (
            "Buongiorno, ho cambiato banca e vorrei aggiornare i miei dati bancari "
            "per il versamento dello stipendio. Il nuovo IBAN è CH93 0076 2011 6238 5295 7. "
            "La banca è UBS. Il titolare del conto sono io."
        ),
        "caller_name": "Marco Rossi",
    },
    {
        "subject": "PRINCE2 Kurs Anfrage",
        "description": (
            "Hallo HR-Team, ich möchte gerne an einem Projektmanagement-Kurs teilnehmen. "
            "Es handelt sich um den 'PRINCE2 Foundation' Kurs bei Digicomp vom 10.-12. April. "
            "Die Kosten betragen CHF 2'400. Mein Vorgesetzter hat mündlich zugestimmt."
        ),
        "caller_name": "Thomas Weber",
    },
    {
        "subject": "Krank - Dauer unbekannt",
        "description": (
            "Hallo, ich fühle mich seit gestern nicht gut und bleibe diese Woche zu Hause. "
            "Ich weiss noch nicht wann ich zurückkomme."
        ),
        "caller_name": "Lisa Brunner",
    },
    {
        "subject": "Allocations familiales - naissance",
        "description": (
            "Bonjour, ma femme vient d'accoucher le 5 février. Notre fils s'appelle Lucas. "
            "Je voudrais demander les allocations familiales. Ci-joint l'acte de naissance."
        ),
        "caller_name": "Jean-Marc Favre",
    },
    {
        "subject": "Frage zum Vertrag",
        "description": (
            "Hallo, ich habe eine Frage zu meinem Vertrag. "
            "Können Sie mich bitte zurückrufen?"
        ),
        "caller_name": "Michael Schmidt",
    },
    {
        "subject": "Reisekostenabrechnung München",
        "description": (
            "Guten Tag, ich war letzte Woche auf Geschäftsreise in München und möchte "
            "meine Reisekosten abrechnen. Hotel: CHF 180/Nacht (2 Nächte), Zugticket: CHF 95. "
            "Die Belege sind beigefügt."
        ),
        "caller_name": "Sandra Huber",
    },
    {
        "subject": "Work Reference Letter Request",
        "description": (
            "Hello, I am applying for a new position externally and would need a work "
            "reference letter. Could you please prepare one in English? I have been with "
            "the company for 4 years in the Marketing department."
        ),
        "caller_name": "David Chen",
    },
    # --- Attachment scenario: valid doctor note (image scan) ---
    {
        "subject": "Maladie - certificat médical joint",
        "description": (
            "Bonjour, je suis malade depuis lundi et ne peux pas travailler cette semaine. "
            "Veuillez trouver ci-joint mon certificat médical scanné."
        ),
        "caller_name": "Lucas Martin",
        "attachments": [VALID_DOCTOR_NOTE_IMAGE],
    },
    # --- Attachment scenario: INVALID - wrong document type (grocery receipt) ---
    {
        "subject": "Krankmeldung - Beleg anbei",
        "description": (
            "Hallo, ich bin krank und habe den Beleg angehängt. "
            "Bitte entschuldigen Sie meine Abwesenheit diese Woche."
        ),
        "caller_name": "Felix Bauer",
        "attachments": [INVALID_RECEIPT_IMAGE],
    },
    # --- Attachment scenario: INVALID - patient name mismatch ---
    {
        "subject": "Sick leave notification with certificate",
        "description": (
            "Hi HR, I'm not feeling well and need to take sick leave. "
            "Attached is my medical certificate. I expect to be back next Monday."
        ),
        "caller_name": "Elena Kowalski",
        "attachments": [MISMATCHED_NAME_CERTIFICATE],
    },
    # --- Attachment scenario: INVALID - expired/old certificate ---
    {
        "subject": "Krankmeldung - Arztzeugnis beigelegt",
        "description": (
            "Guten Tag, ich bin diese Woche krank. Anbei finden Sie mein Arztzeugnis. "
            "Ich hoffe, nächste Woche wieder fit zu sein."
        ),
        "caller_name": "Thomas Weber",
        "attachments": [EXPIRED_CERTIFICATE],
    },
    # --- Attachment scenario: SUSPICIOUS - fictitious doctor (not findable via web) ---
    {
        "subject": "Krankmeldung - 2 Wochen Ausfall",
        "description": (
            "Hallo HR-Team, ich bin leider für die nächsten zwei Wochen krank geschrieben. "
            "Das Arztzeugnis habe ich angehängt. Bitte um Bestätigung."
        ),
        "caller_name": "Stefan Gruber",
        "attachments": [FICTITIOUS_DOCTOR_CERTIFICATE],
    },
    # --- Attachment scenario: SUSPICIOUS - fake clinic in Geneva ---
    {
        "subject": "Arrêt maladie - certificat joint",
        "description": (
            "Bonjour, je suis en arrêt maladie depuis lundi. "
            "Ci-joint le certificat médical de mon médecin. "
            "Je reviendrai au bureau le 2 juin."
        ),
        "caller_name": "Marie Lefevre",
        "attachments": [FAKE_CLINIC_CERTIFICATE],
    },
    # --- Attachment scenario: VALID - verifiable university hospital ---
    {
        "subject": "Krankheit - Arztzeugnis USZ",
        "description": (
            "Guten Tag, ich war im Universitätsspital Zürich und bin für eine Woche "
            "krankgeschrieben worden. Das Zeugnis ist anbei."
        ),
        "caller_name": "Katrin Hofmann",
        "attachments": [VALID_CERTIFICATE_VERIFIABLE],
    },
    # --- Attachment scenario: SUSPICIOUS - GLN doesn't match doctor name ---
    {
        "subject": "Teilkrankmeldung 50% - Arztzeugnis",
        "description": (
            "Hallo, ich bin zu 50% arbeitsunfähig geschrieben worden. "
            "Das Arztzeugnis meines Hausarztes finden Sie im Anhang. "
            "Ich werde morgens von zu Hause arbeiten."
        ),
        "caller_name": "Rolf Meier",
        "attachments": [GLN_MISMATCH_CERTIFICATE],
    },
]
