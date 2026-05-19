"""Synthetic attachment data for testing document analysis.

Provides simulated attachment metadata and extracted text content for tickets
that have attachments (e.g., medical certificates for sick leave).
"""

# Simulated attachment metadata and OCR/extracted text for seed tickets.
# In production, this would come from Azure Document Intelligence or similar.

ATTACHMENTS: dict[str, list[dict]] = {}

# --- Valid medical certificate (PDF) for sick leave ticket ---
VALID_DOCTOR_NOTE_PDF = {
    "filename": "arztzeugnis_mueller_2026.pdf",
    "content_type": "application/pdf",
    "size_bytes": 45230,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Praxis Dr. med. Hans Berger\n"
        "Bahnhofstrasse 42, 8001 Zürich\n"
        "Tel: +41 44 123 45 67\n\n"
        "Patient/in: Anna Müller\n"
        "Geburtsdatum: 15.03.1990\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 23.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Hans Berger\n"
        "GLN: 7601000000001"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_mueller_2026.pdf",
}

# --- Invalid attachment: grocery receipt instead of doctor note ---
INVALID_RECEIPT_IMAGE = {
    "filename": "IMG_20260519_receipt.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 128450,
    "extracted_text": (
        "MIGROS\n"
        "Filiale Zürich Hauptbahnhof\n"
        "Datum: 19.05.2026  14:32\n\n"
        "Vollmilch 1L          2.95\n"
        "Brot Ruchbrot          3.40\n"
        "Bananen 1kg            2.80\n"
        "Mineralwasser 6x      6.50\n"
        "Jogurt Nature          1.20\n\n"
        "TOTAL                 16.85\n"
        "Bezahlt: Debitkarte\n"
        "Vielen Dank für Ihren Einkauf!"
    ),
    "url": "https://servicedesk.example.com/attachments/IMG_20260519_receipt.jpg",
}

# --- Valid medical certificate (image/scan) ---
VALID_DOCTOR_NOTE_IMAGE = {
    "filename": "krankmeldung_scan.png",
    "content_type": "image/png",
    "size_bytes": 234500,
    "extracted_text": (
        "ARZTZEUGNIS / CERTIFICAT MÉDICAL\n\n"
        "Dr. med. Claire Fontaine\n"
        "Cabinet médical du Lac\n"
        "Rue du Lac 8, 1003 Lausanne\n"
        "Tél: +41 21 987 65 43\n\n"
        "Patient: Lucas Martin\n"
        "Date de naissance: 22.08.1985\n\n"
        "Date de consultation: 18.05.2026\n\n"
        "Je certifie que le patient susmentionné est en incapacité de travail\n"
        "pour raisons médicales.\n\n"
        "Incapacité: 100%\n"
        "Du: 18.05.2026\n"
        "Au: 25.05.2026\n\n"
        "Signature et cachet\n"
        "Dr. med. Claire Fontaine\n"
        "RCC: Z123456"
    ),
    "url": "https://servicedesk.example.com/attachments/krankmeldung_scan.png",
}

# --- Invalid: certificate with wrong patient name ---
MISMATCHED_NAME_CERTIFICATE = {
    "filename": "arztzeugnis_other_person.pdf",
    "content_type": "application/pdf",
    "size_bytes": 52100,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Peter Roth\n"
        "Marktgasse 12, 3011 Bern\n"
        "Tel: +41 31 456 78 90\n\n"
        "Patient/in: Markus Schneider\n"
        "Geburtsdatum: 05.11.1988\n\n"
        "Datum der Konsultation: 17.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 50%\n"
        "Von: 17.05.2026\n"
        "Bis: 24.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Peter Roth\n"
        "GLN: 7601000000099"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_other_person.pdf",
}

# --- Invalid: expired/old certificate ---
EXPIRED_CERTIFICATE = {
    "filename": "old_certificate_jan2025.pdf",
    "content_type": "application/pdf",
    "size_bytes": 38900,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Maria Keller\n"
        "Steinenvorstadt 5, 4051 Basel\n"
        "Tel: +41 61 234 56 78\n\n"
        "Patient/in: Thomas Weber\n"
        "Geburtsdatum: 30.06.1982\n\n"
        "Datum der Konsultation: 10.01.2025\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 10.01.2025\n"
        "Bis: 17.01.2025\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Maria Keller\n"
        "GLN: 7601000000050"
    ),
    "url": "https://servicedesk.example.com/attachments/old_certificate_jan2025.pdf",
}

# --- INVALID: Completely fictitious doctor (not findable via web search) ---
FICTITIOUS_DOCTOR_CERTIFICATE = {
    "filename": "arztzeugnis_suspicious.pdf",
    "content_type": "application/pdf",
    "size_bytes": 41200,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Xaver Phantomberg\n"
        "Geisterallee 999, 0000 Nirgendwo\n"
        "Tel: +41 00 000 00 00\n\n"
        "Patient/in: Stefan Gruber\n"
        "Geburtsdatum: 14.09.1991\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 30.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Xaver Phantomberg\n"
        "GLN: 0000000000000"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_suspicious.pdf",
}

# --- INVALID: Fake clinic with non-existent address ---
FAKE_CLINIC_CERTIFICATE = {
    "filename": "medical_cert_fakeclinic.pdf",
    "content_type": "application/pdf",
    "size_bytes": 39800,
    "extracted_text": (
        "CERTIFICAT MÉDICAL\n\n"
        "Dr. Jean-Baptiste Inexistant\n"
        "Clinique Fantôme SA\n"
        "Chemin des Nuages 42, 1200 Genève\n"
        "Tél: +41 22 000 00 00\n\n"
        "Patient: Marie Lefevre\n"
        "Date de naissance: 03.07.1995\n\n"
        "Date de consultation: 18.05.2026\n\n"
        "Je certifie que le patient susmentionné est en incapacité de travail\n"
        "pour raisons médicales.\n\n"
        "Incapacité: 100%\n"
        "Du: 18.05.2026\n"
        "Au: 01.06.2026\n\n"
        "Signature et cachet\n"
        "Dr. Jean-Baptiste Inexistant\n"
        "RCC: X000000"
    ),
    "url": "https://servicedesk.example.com/attachments/medical_cert_fakeclinic.pdf",
}

# --- Valid certificate with real-sounding doctor (verifiable) ---
VALID_CERTIFICATE_VERIFIABLE = {
    "filename": "zeugnis_universitaetsspital.pdf",
    "content_type": "application/pdf",
    "size_bytes": 56700,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Universitätsspital Zürich\n"
        "Klinik für Allgemeine Innere Medizin\n"
        "Rämistrasse 100, 8091 Zürich\n"
        "Tel: +41 44 255 11 11\n\n"
        "Behandelnder Arzt: Dr. med. Stefan Mayer\n\n"
        "Patient/in: Katrin Hofmann\n"
        "Geburtsdatum: 22.04.1988\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 26.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Stefan Mayer\n"
        "Universitätsspital Zürich\n"
        "GLN: 7601000618627"
    ),
    "url": "https://servicedesk.example.com/attachments/zeugnis_universitaetsspital.pdf",
}

# --- Suspicious: valid-looking cert but GLN doesn't match doctor name ---
GLN_MISMATCH_CERTIFICATE = {
    "filename": "arztzeugnis_gln_mismatch.pdf",
    "content_type": "application/pdf",
    "size_bytes": 44100,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Andreas Widmer\n"
        "Praxis am See\n"
        "Seestrasse 15, 6004 Luzern\n"
        "Tel: +41 41 345 67 89\n\n"
        "Patient/in: Rolf Meier\n"
        "Geburtsdatum: 11.12.1979\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 50%\n"
        "Von: 19.05.2026\n"
        "Bis: 02.06.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Andreas Widmer\n"
        "GLN: 7601000000001"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_gln_mismatch.pdf",
}
